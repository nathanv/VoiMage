#include <pocketsphinx.h>
//#define WIN32 1

#ifndef WIN32
#include<signal.h>
#endif

ps_decoder_t *ps;
FILE *fh;
FILE *outfile;

void signal_handler(int signum) {
  if (fh != NULL)
    fclose(fh);
  if (outfile != NULL)
    fclose(outfile);
  if (ps_free != NULL)
    ps_free(ps);
  exit(0);
}

int main(int argc, char *argv[]) {
	cmd_ln_t *config;
	char const *hyp, *uttid;
        int16 buf[512];
  char *outfname = NULL;
	int rv;
  int i = 1;
	int32 score;
#ifndef WIN32
  signal(SIGINT, signal_handler);
  signal(SIGTERM, signal_handler);
#endif

	config = cmd_ln_init(NULL, ps_args(), TRUE,
			     "-hmm", MODELDIR "/hmm/en_US/hub4wsj_sc_8k", //sample general english dictionaries
			     "-lm", MODELDIR "/lm/en/turtle.DMP",
			     "-dict", MODELDIR "/lm/en/turtle.dic",
			     NULL);
	if (config == NULL)
		return 1;
	ps = ps_init(config);
	if (ps == NULL)
		return 1;
  if (argc < 2) {
    printf("%d", argc);
    perror("Need a command file to open");
    ps_free(ps);
    return 1;
  }
  outfname = argv[1];
  outfile = fopen(outfname, "w");
  if (outfile == NULL) {
    perror("Failed to open output file");
    return 1;
  }

  while(i) { //loop until program terminates

    fh = fopen("open.raw", "rb"); //matches against recorded sample
    if (fh == NULL) {
      perror("Failed to open open.raw");
      return 1;
    }
    rv = ps_decode_raw(ps, fh, "open", -1);
    if (rv < 0) {
      perror("oopslol!");
      return 1;
    }
    hyp = ps_get_hyp(ps, &score, &uttid);
    if (hyp == NULL) {
      perror("no hypothesis!");
    } else {
      fprintf(outfile, "Recognized: %s\n", hyp);
    }
    fclose(fh);
    fh = NULL;
    sleep(1);
  }

  fclose(outfile);
  outfile = NULL;
  ps_free(ps);
	return 0;
}

