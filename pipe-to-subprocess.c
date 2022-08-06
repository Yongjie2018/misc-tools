#include <stdio.h>
#include <stdlib.h>

void
read_data (FILE * stream)
{
  unsigned char buff[1025];
  size_t len;

  do {
    len = fread(buff, 1, sizeof(buff) - 1, stream);
    if (len > 0)
    {
      buff[len] = '\0';
      puts(buff);
    }
  } while (!feof(stream));
}

int
main (void)
{
  FILE *output;

  output = popen ("journalctl -t 0", "r");
  if (!output)
    {
      fprintf (stderr,
               "incorrect parameters or too many files.\n");
      return EXIT_FAILURE;
    }
  read_data (output);
  if (pclose (output) != 0)
    {
      fprintf (stderr,
               "Could not run more or other error.\n");
    }
  return EXIT_SUCCESS;
}

