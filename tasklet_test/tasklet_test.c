/***************************************************************************//**
*  \file       driver.c
*
*  \details    Simple Linux device driver (Kernel Thread)
*
*  \author     EmbeTronicX
*
*  \Tested with Linux raspberrypi 5.10.27-v7l-embetronicx-custom+
*
*******************************************************************************/
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kdev_t.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/slab.h>                 //kmalloc()
#include <linux/uaccess.h>              //copy_to/from_user()
#include <linux/kthread.h>             //kernel threads
#include <linux/sched.h>               //task_struct 
#include <linux/delay.h>
#include <linux/err.h>
#include <linux/cpumask.h>
#include <linux/interrupt.h>
#include <linux/printk.h>
#include <asm/msr.h>

#define MAX_CPU_NUM 512
#define TASKLET_NUM_PER_CPU 1024

struct tsc_pair {
        int cpu_id, curr_cpu_id;
        uint8_t valid;
        uint64_t tsc1, tsc2;
};

dev_t dev = 0;
static struct class *dev_class;
static struct cdev etx_cdev;
 
static int __init etx_driver_init(void);
static void __exit etx_driver_exit(void);
 
static struct task_struct *etx_thread[MAX_CPU_NUM];
static struct tsc_pair *etx_tsc[MAX_CPU_NUM];
static int ncpu = 0;

static struct tasklet_struct *tasklet[MAX_CPU_NUM];

/*
** Function Prototypes
*/
/*************** Driver functions **********************/
static int etx_open(struct inode *inode, struct file *file);
static int etx_release(struct inode *inode, struct file *file);
static ssize_t etx_read(struct file *filp, 
                char __user *buf, size_t len,loff_t * off);
static ssize_t etx_write(struct file *filp, 
                const char *buf, size_t len, loff_t * off);
 /******************************************************/

/*Tasklet Function*/
void tasklet_fn(unsigned long arg)
{
    int cpu_id = arg >> 32;
    int i = arg & 0xFFFFFFFF;
    etx_tsc[cpu_id][i].tsc2 = rdtsc();
    etx_tsc[cpu_id][i].curr_cpu_id = smp_processor_id();
}

int thread_function(void *pv);
/*
** Thread
*/
int thread_function(void *pv)
{
    struct tsc_pair *ptsc = pv;
    int i;
    int cpu_id;

    cpu_id = ptsc[0].cpu_id;
    tasklet[cpu_id] = kmalloc(sizeof(struct tasklet_struct) * TASKLET_NUM_PER_CPU, GFP_KERNEL);
    if (NULL == tasklet[cpu_id]) {
        printk(KERN_INFO "cannot allocate memory");
        return 1;
    }
    for (i = 0; i < TASKLET_NUM_PER_CPU; i++)
    {
        uint64_t d = ptsc[0].cpu_id;
        d = (d << 32) | i;
        tasklet_init(tasklet[ptsc[i].cpu_id] + i, tasklet_fn, d);
    }

    while(!kthread_should_stop()) {
        for (i = 0; i < TASKLET_NUM_PER_CPU; i++)
        {
                int cpu_changed = ptsc[i].cpu_id != smp_processor_id();
                //pr_info("In EmbeTronicX Thread %lld %d\n", ptsc->cpu_id, i++);
                if (!cpu_changed)
                {
                    ptsc[i].valid = 1;
                    ptsc[i].tsc2 = 0;
                    ptsc[i].tsc1 = rdtsc();
                    
                    tasklet_schedule(tasklet[ptsc[i].cpu_id] + i);
                }
                else
                    ptsc[i].valid = 0;
        }
        msleep(1);
        for (i = 0; i < TASKLET_NUM_PER_CPU; i++)
        {
                if (0 != ptsc[i].valid && ptsc[i].tsc2 != 0)
                    pr_info("[%d:%d:%d] %llu\n", ptsc[i].cpu_id, ptsc[i].curr_cpu_id, i, ptsc[i].tsc2 - ptsc[i].tsc1);
        }
    }

    if (NULL != tasklet[cpu_id]) {
        kfree(tasklet[cpu_id]);
    }
    return 0;
}

/*
** File operation sturcture
*/ 
static struct file_operations fops =
{
        .owner          = THIS_MODULE,
        .read           = etx_read,
        .write          = etx_write,
        .open           = etx_open,
        .release        = etx_release,
};
/*
** This function will be called when we open the Device file
*/  
static int etx_open(struct inode *inode, struct file *file)
{
        pr_info("Device File Opened...!!!\n");
        return 0;
}
/*
** This function will be called when we close the Device file
*/   
static int etx_release(struct inode *inode, struct file *file)
{
        pr_info("Device File Closed...!!!\n");
        return 0;
}
/*
** This function will be called when we read the Device file
*/
static ssize_t etx_read(struct file *filp, 
                char __user *buf, size_t len, loff_t *off)
{
        pr_info("Read function\n");
 
        return 0;
}
/*
** This function will be called when we write the Device file
*/
static ssize_t etx_write(struct file *filp, 
                const char __user *buf, size_t len, loff_t *off)
{
        pr_info("Write Function\n");
        return len;
}

/*
** Module Init function
*/  
static int __init etx_driver_init(void)
{
        int i, j;

        /*Allocating Major number*/
        if((alloc_chrdev_region(&dev, 0, 1, "etx_Dev")) <0){
                pr_err("Cannot allocate major number\n");
                return -1;
        }
        pr_info("Major = %d Minor = %d \n",MAJOR(dev), MINOR(dev));
 
        /*Creating cdev structure*/
        cdev_init(&etx_cdev,&fops);
 
        /*Adding character device to the system*/
        if((cdev_add(&etx_cdev,dev,1)) < 0){
            pr_err("Cannot add the device to the system\n");
            goto r_class;
        }
 
        /*Creating struct class*/
        if(IS_ERR(dev_class = class_create(THIS_MODULE,"etx_class"))){
            pr_err("Cannot create the struct class\n");
            goto r_class;
        }
 
        /*Creating device*/
        if(IS_ERR(device_create(dev_class,NULL,dev,NULL,"etx_device"))){
            pr_err("Cannot create the Device \n");
            goto r_device;
        }

        ncpu = num_online_cpus();
        for (i = 0; i < ncpu; i++)
        {
            etx_tsc[i] = kmalloc(sizeof(struct tsc_pair) * TASKLET_NUM_PER_CPU, GFP_KERNEL);
            for (j = 0; j < TASKLET_NUM_PER_CPU; j++)
                etx_tsc[i][j].cpu_id = i;
            etx_thread[i] = kthread_create(thread_function, etx_tsc[i],"eTx Thread %d", i);
            if(etx_thread[i]) {
                kthread_bind(etx_thread[i], i);
                wake_up_process(etx_thread[i]);
            } else {
                pr_err("Cannot create kthread\n");
                goto r_device;
            }
        }
#if 0
        /* You can use this method also to create and run the thread */
        etx_thread = kthread_run(thread_function,NULL,"eTx Thread");
        if(etx_thread) {
            pr_info("Kthread Created Successfully...\n");
        } else {
            pr_err("Cannot create kthread\n");
             goto r_device;
        }
#endif

        pr_info("Device Driver Insert...Done!!!\n");
        return 0;
 
 
r_device:
        class_destroy(dev_class);
r_class:
        unregister_chrdev_region(dev,1);
        cdev_del(&etx_cdev);
        return -1;
}
/*
** Module exit function
*/  
static void __exit etx_driver_exit(void)
{
        int i;
        msleep(1000);
        for (i = 0; i < ncpu; i++)
        {
            kthread_stop(etx_thread[i]);
            if (etx_tsc[i])
                kfree(etx_tsc[i]);
        }
        device_destroy(dev_class,dev);
        class_destroy(dev_class);
        cdev_del(&etx_cdev);
        unregister_chrdev_region(dev, 1);
        pr_info("Device Driver Remove...Done!!\n");
}
 
module_init(etx_driver_init);
module_exit(etx_driver_exit);
 
MODULE_LICENSE("GPL");
MODULE_AUTHOR("EmbeTronicX <embetronicx@gmail.com>");
MODULE_DESCRIPTION("A simple device driver - Kernel Thread");
MODULE_VERSION("1.14");

