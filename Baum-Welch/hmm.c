/*  
 * Train text on a two-state HMM using Baum-Welch algorithm               
 *          
 *      @author yatbear <sapphirejyt at gmail dot com>                                 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <math.h>

#define VOCAB_SIZE 27 // vocabulary size
#define STATE_SIZE 2  // number of states
#define ASIZE 30000   // number of letters in training file A
#define BSIZE 5000    // number of letters in test file B

int N;  // stage number
int *V; // letter array
double p[STATE_SIZE][STATE_SIZE]; // transition probabilities between states
double q[VOCAB_SIZE][STATE_SIZE]; // emission probabilities of states 
double alpha[ASIZE][STATE_SIZE];  // forward probabilities
double beta[ASIZE][STATE_SIZE];   // backward probabilities
double gammas[ASIZE][STATE_SIZE];
double sigma[ASIZE][STATE_SIZE][STATE_SIZE];

/* Read text A and text B into arrays */
void readFile(char const* filename, int size){
    FILE *file;
    int BUFSIZE = 128;
    char cwd[BUFSIZE];
    strcat(getcwd(cwd, sizeof(cwd)), filename);
    file = fopen(cwd, "rt");
    if(!file){
        printf("Error accessing the file.");
        exit(1);
    }
    /* Use an int array to store the letters from the files */
    V = (int*) malloc(size * sizeof(int)); 
    int readch = 0;
    int count = 0;
    while((readch = fgetc(file)) != EOF){
        if(isalpha(readch))
            V[count] = readch - 97; // ASCII value - 96 - 1 
        else 
            V[count] = 26; // space
        count++;
    }

    fclose(file);
    return;
}

/* Initializa p and q */
void initParameters(){
    p[0][1] = p[1][0] = log(0.51);
    p[0][0] = p[1][1] = log(0.49);

    for(int i=0; i<13; i++){
        q[i][0] = log(0.0370);
        q[i][1] = log(0.0371);
    }
    for(int i=13; i<26; i++){
        q[i][0] = log(0.0371);
        q[i][1] = log(0.0370);
    }
    q[26][0] = q[26][1] = log(0.0367);
    
    return;
}

/* Compute log(x+1) efficiently */
double logOnePlus(double x){
    if(x <= -1.0){
        printf("Invalid argument");
        exit(1);
    }
    if(fabs(x) > 1e-4)
        return log(1.0 + x);
    return (-0.5 * x + 1.0) * x;
}

/* Compute log(x+y) efficiently */
double logAdd(double x, double y){
    return y<=x ? x + logOnePlus(exp(y-x)) : y + logOnePlus(exp(x-y));
}

/* Compute alpha */
void forward(){
    for(int i=0; i<N; i++){
        int v = V[i];
        double C = log(0.0);
        for(int s=0; s<STATE_SIZE; s++){
            alpha[i][s] = log(0.0);
            for(int s0=0; s0<STATE_SIZE; s0++){
                double alpha0 = i==0 ? log(0.5) : alpha[i-1][s0]; 
                double delta = alpha0 + p[s0][s] + q[v][s];
                alpha[i][s] = logAdd(alpha[i][s], delta);
            }
            C = logAdd(C, alpha[i][s]);
        }
        /* Normalize alpha */
        for(int s=0; s<STATE_SIZE; s++) 
            alpha[i][s] -= C;   
    }
    return;
}

/* Compute beta */
void backward(){
    for(int i=N-1; i>=0; i--){
        int v = V[i+1];
        double C = log(0.0);
        for(int s=0; s<STATE_SIZE; s++){
            beta[i][s] = log(0.0);
            for(int s1=0; s1<STATE_SIZE; s1++){
                double beta1 = i==N-1 ? log(1.0) : beta[i+1][s1];
                double delta = beta1 + p[s][s1] + q[v][s1];
                beta[i][s] = logAdd(beta[i][s], delta);
            }
            C = logAdd(C, beta[i][s]);
        }
        /* Normalize beta */
        for(int s=0; s<STATE_SIZE; s++)
            beta[i][s] -= C;    
    }
    return;
}

/* Compute gamma and sigma */
void compute_Gamma_Sigma(){
    /* Compute gamma */
    for(int i=0; i<N; i++){
        double C = log(0.0);
        for(int s=0; s<STATE_SIZE; s++){
            gammas[i][s] = alpha[i][s] + beta[i][s];
            C = logAdd(C, gammas[i][s]);
        }
        /* Normalize gamma */
        for(int s=0; s<STATE_SIZE; s++) 
            gammas[i][s] -= C;

        if(i == N-1) 
            return;

        /* Compute sigma */
        int v = V[i+1];
        C = log(0.0);
        for(int s=0; s<STATE_SIZE; s++){
            for(int s1=0; s1<STATE_SIZE; s1++){
                sigma[i][s][s1] = alpha[i][s] + p[s][s1] + q[v][s1] + beta[i+1][s1];
                C = logAdd(C, sigma[i][s][s1]);
            }
        }
        /* Normalize sigma */
        for(int s=0; s<STATE_SIZE; s++)
            for(int s1=0; s1<STATE_SIZE; s1++)
                sigma[i][s][s1] -= C;
    }
    return;
}

/* Reestimate model parameters p and q */
void reestimate(){
    double gamma_sum[STATE_SIZE];
    double sigma_sum[STATE_SIZE][STATE_SIZE];
    /* Collect counts */
    for(int s=0; s<STATE_SIZE; s++){
        for(int s1=0; s1<STATE_SIZE; s1++){
            sigma_sum[s][s1] = log(0.0);
            gamma_sum[s1] = log(0.0); 
            for(int i=0; i<N; i++){
                gamma_sum[s1] = logAdd(gamma_sum[s1], gammas[i][s1]);
                if(i < N-1)
                    sigma_sum[s][s1] = logAdd(sigma_sum[s][s1], sigma[i][s][s1]);
            }
        }
    }

    /* Reestimate transition probabilities */
    for(int s=0; s<STATE_SIZE; s++) 
        for(int s1=0; s1<STATE_SIZE; s1++) 
            p[s][s1] = sigma_sum[s][s1] - gamma_sum[s];

    /* Reestimate emission probabilities */
    for(int v=0; v<VOCAB_SIZE; v++)
        for(int s=0; s<STATE_SIZE; s++)
            q[v][s] = log(0.0);
        
    for(int i=0; i<N; i++){
        int v = V[i];
        for(int s=0; s<STATE_SIZE; s++){
            double delta = gammas[i][s] - gamma_sum[s];
            q[v][s] = logAdd(q[v][s], delta);
        }
    }
    return;
}

/* Train HMM */
void train(int iter_time){
    N = ASIZE;
    readFile("/data/textA", ASIZE);
    initParameters();
    for(int k=0; k<iter_time; k++){
        forward();
        backward();
        compute_Gamma_Sigma();
        reestimate();
    }
    return;
}

int main(void){
    int k = 600; // iteration time
    train(k);

    printf("Transition probabilities:\n");
    for(int s=0; s<STATE_SIZE; s++) 
        for(int s1=0; s1<STATE_SIZE; s1++)
            printf("state %d -> state %d  %f\n", s+1, s1+1, exp(p[s][s1]));

    printf("\nEmission probabilities:\n");
    for(int v=0; v<VOCAB_SIZE; v++)
        for(int s=0; s<STATE_SIZE; s++){
            char c = v == 26 ? ' ' : v + 97; // convert ASCII value back to letter
            printf("state %d : %c  %f\n", s+1, c, exp(q[v][s]));
        }

    return 0;
}
