/* demo.c */

#include "lp_lib.h"

double rateE;

#define MAX_SIZE 1024
///// Latencies of memories (referred from Transactional NVM Cache paper of SC'17)
#define DRAM_LAT 100 
#define NVM_LAT 200

///// Capacities of memories (referred from Transactional NVM Cache paper of SC'17)
///// Unit : B / 4096

//#define DRAM_SIZE 65536  // 0.25GB / 4KB
//#define DRAM_SIZE 131072  // 0.5GB / 4KB
//#define DRAM_SIZE 262144  // 1GB / 4KB
#define DRAM_SIZE 524288  // 2GB / 4KB
//#define DRAM_SIZE 1048576  // 4GB / 4KB
//#define DRAM_SIZE 2097152  // 8GB / 4KB
#define NVM_SIZE 4194304  // 16GB / 4KB

//#define DRAM_SIZE 130  // 0.5GB / (4KB * 1K)
//#define DRAM_SIZE 256  // 1GB / (4KB * 1K)
//#define DRAM_SIZE 512  // 2GB / (4KB * 1K)
//#define DRAM_SIZE 1024  // 4GB / (4KB * 1K)
//#define DRAM_SIZE 2048  // 8GB / (4KB * 1K)
//#define NVM_SIZE 4096  // 16GB / (4KB * 1K)

///// The rate required to meet

int *var_placement; // Placement of major variables
int variable_count = 0;

FILE *fp_out;
struct _variable
{
  unsigned long hash;
  int size;
  int accessed;
  double Ed;
  double Es_s;
  double Es_p;
  int dc_4k;
  int dc_20m;
  int dc_llc_mpki;
} variables[MAX_SIZE];

inline int DecidePlacement() 
{
  lprec *lp;
  int Ncol, *colno = NULL, ret = 1, i;
  char varName[3] = {0,};
  REAL *row = NULL;

  Ncol = variable_count;
  lp = make_lp(0, Ncol);
  if (lp == NULL) {
    ret = 0;
    printf("{Err - 1] make_lp returns NULL!\n");
  }

  if (ret) {
    for (i = 1; i <= Ncol; i++) {
      sprintf(varName, "x%d", i);
      if (!set_col_name(lp, i, varName)) {   //// Set variables
        ret = 0;
        printf("[Err - 2] set_col_name returns False!\n");
      }
      if (!set_int(lp, i, TRUE)) {  //// Bound variables to be only integers
        ret = 0;
        printf("[Err - 3] set_int returns False!\n");
      }
    }

    colno = (int*) malloc(Ncol * sizeof(*colno));
    var_placement = (int*) malloc(Ncol * sizeof(*var_placement));
    row = (REAL*) malloc(Ncol * sizeof(*row));

    if ((colno == NULL) || (row == NULL)) {
      ret = 0;
      printf("[Err - 4] malloc on colno / row returns error!\n");
    }
  }

  if (ret) {
    set_add_rowmode(lp, TRUE);

    ///// 1. Decision constraint : All decisions must be 0 or 1
    for (i = 0; i < Ncol; i++) {
      colno[0] = i+1;
      row[0] = 1;
      if (!add_constraintex(lp, 1, row, colno, GE, 0)) {
        ret = 0;
        printf("[Err - 5] add_constraintex for decision( > 0) returns error!\n");
      }
      if (!add_constraintex(lp, 1, row, colno, LE, 1)) {
        ret = 0;
        printf("[Err - 5] add_constraintex for decision( < 1) returns error!\n");
      }
    }
  }

  if (ret) {
    set_add_rowmode(lp, TRUE);

    ///// 2. Capacity constraints : Size of all variables must not exceed memories sizes
    for (i = 0; i < Ncol; i++) {
      colno[i] = i+1;
      row[i] = variables[i].size;
    }

    if (!add_constraintex(lp, Ncol, row, colno, LE, DRAM_SIZE)) {
      ret = 0;
      printf("[Err - 6] add_constraintex for capacity ( < DRAM_SIZE) returns error!\n");
    }
    
    // Add the constraint for NVM later
     
  }

  if (ret) {
    double E_dram = 0, E_nvm = 0;
    int rh = 0;
    set_add_rowmode(lp, TRUE);

    //// 3. Energy constraints : Total energy consumption must not exceed the required energy
    for (i = 0; i < Ncol; i++) {
      colno[i] = i+1;
      row[i] = (int)(variables[i].Ed - variables[i].Es_p);
      //rh += ( (int)(variables[i].Ed * REQ_RATE - variables[i].Es_p));
      E_dram += variables[i].Ed;
      E_nvm += variables[i].Es_p;
    }
    rh = (int)(E_dram*rateE - E_nvm);

    if (!add_constraintex(lp, Ncol, row, colno, LE, rh)) {
      ret = 0;
      printf("[Err - 7] add_constraintex for energy ( < Ed*R) returns error!\n");
    }
  }

  if (ret) {
    set_add_rowmode(lp, FALSE);

    for (i = 0; i < Ncol; i++) {
      colno[i] = i+1;
      //row[i] = (int)((DRAM_LAT - NVM_LAT) * variables[i].accessed);
      //row[i] = (int)((DRAM_LAT - NVM_LAT) * variables[i].dc_4k);
      //row[i] = (int)((DRAM_LAT - NVM_LAT) * variables[i].dc_20m);
      row[i] = (int)((DRAM_LAT - NVM_LAT) * variables[i].dc_llc_mpki);
    }

    if (!set_obj_fnex(lp, Ncol, row, colno)) {
      ret = 0;
      printf("[Err - 8] set_obj_fnex optimize function returns error!\n");
    }
  }

  if (ret) {
    set_minim(lp);  // Optimization is minimization

    write_LP(lp, stdout);  // Set verbose only for console application
    set_verbose(lp, IMPORTANT);  // Verbose option

    ret = solve(lp);
    if (ret == OPTIMAL) {
      ret = 1;
      printf("[Solver] Optimal case is derived!\n");
    }
    else {
      printf("[Solver] Infeasible constraint!\n");
    }
  }

  if (ret) {

    double sumLat = 0, sumEnergy = 0, allDRAM_E = 0;
    for (i = 0; i < Ncol; i++)
      sumLat += variables[i].dc_llc_mpki;
      //sumLat += variables[i].accessed;
    printf("Objective value: %d\n", (int)get_objective(lp) + NVM_LAT*(int)sumLat);

    if (!get_variables(lp, row)) {
      ret = 0;
      printf("[Err - 9] get_variables returns error!\n");
    }
    
    for (i = 0; i < Ncol; i++) {
      allDRAM_E += variables[i].Ed;

      if (row[i]) {
        sumEnergy += variables[i].Ed;
        fprintf(fp_out, "%lu\n1\n", variables[i].hash);
        //printf("%d-th variable : DRAM\n", i);
        printf("%lu-th variable : DRAM\n", variables[i].hash);
        //printf("1\n");
      }
      else {
        sumEnergy += variables[i].Es_p;
        fprintf(fp_out, "%lu\n0\n", variables[i].hash);
        //printf("%d-th variable : STT-RAM\n", i);
        printf("%lu-th variable : NVM\n", variables[i].hash);
        //printf("0\n");
      }

    } 
    fprintf(stderr,"All-DRAM energy : %d\n", (int)allDRAM_E);
    fprintf(stderr,"Rate : %.2f, Required energy : %d\n", rateE, (int)(rateE*allDRAM_E));
    fprintf(stderr,"Expected energy : %d\n", (int)sumEnergy);

  }
  
  if (row != NULL) free(row);
  if (colno != NULL) free(colno);
  
  return ret;
}

int main(int argc, char *argv[])
{
  if (argc < 2) {
    printf("Input argument for energy constraint ratio!\n");
    return 0;
  }
    
  sscanf(argv[1], "%lf", &rateE);
  int i = 0;
  FILE *fp = fopen("data.energy", "r");
  FILE *fp2 = fopen("data.4k_cache", "r");
  FILE *fp3 = fopen("data.20m_cache", "r");
  FILE *fp4 = fopen("data.llc_mpki", "r");
  fp_out = fopen("data.placement", "w");

  printf("fp\n");
  while (!feof(fp)) {
    printf("enter while loop!\n");
    fscanf(fp, "%lu\n%d\n%d\n%lf\n%lf\n%lf\n", &(variables[i].hash), &(variables[i].size), &(variables[i].accessed), &(variables[i].Ed), &(variables[i].Es_s), &(variables[i].Es_p));
    i++;
    variable_count++;
  }
  i = 0;
  printf("fp2\n");
  while (!feof(fp2)) {
    fscanf(fp2, "%d\n", &(variables[i].dc_4k));
    i++;
  }
  i = 0;
  printf("fp3\n");
  while (!feof(fp3)) {
    fscanf(fp3, "%d\n", &(variables[i].dc_20m));
    i++;
  }
  i = 0;
  printf("fp4\n");
  while (!feof(fp4)) {
    fscanf(fp4, "%d\n", &(variables[i].dc_llc_mpki));
    i++;
  }

  printf("Total variable : %d\n", variable_count);
  fclose(fp);
  fclose(fp2);
  fclose(fp3);
  fclose(fp4);

  DecidePlacement();
  fclose(fp_out);

  return 0;
}
