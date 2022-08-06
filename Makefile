
all: my-printenv walk-lpu exit-code pipe-to-subprocess err-by-signal


clean:
	rm -f my-printenv walk-lpu exit-code pipe-to-subprocess err-by-signal


my-printenv: my-printenv.c
	gcc -Wall $^ -o $@

err-by-signal: err-by-signal.c
	gcc -Wall  $^ -o $@ -lrt

exit-code: exit-code.c
	gcc -Wall $^ -o $@

walk-lpu: walk-lpu.c
	gcc -Wall $^ -o $@

pipe-to-subprocess: pipe-to-subprocess.c
	gcc -Wall $^ -o $@
