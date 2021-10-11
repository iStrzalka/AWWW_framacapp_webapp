#include <stdio.h>
#define N 10
#define M 10

int suma(int N, int M, int tab[N][M], int nr_kol)
{
    int *pointer = tab[N];
    int suma = 0;
    for(int i = 0; i < N; i++)
    {
        suma += *(*(pointer + nr_kol) + i);
    }
    return suma;
}

int main()
{
    int nr_kol; 
    scanf("%i", nr_kol);
    int tab[N][M];
    printf("%i", suma(N, M, tab[N][M], nr_kol);
}