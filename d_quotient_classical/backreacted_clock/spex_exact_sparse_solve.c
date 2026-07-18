/* Generic exact sparse solve helper for a row-cleared integer CSC system.

   Input format:
     n nnz
     p[0] ... p[n]
     i[0] ... i[nnz-1]
     x[0] ... x[nnz-1]       (one arbitrary-size integer per token)
     b[0] ... b[n-1]         (one arbitrary-size integer per token)

   Output is one canonical rational per line.  The helper is intentionally
   independent of the Berger calculation; Python constructs and later replays
   the exact system.
*/

#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

#include <SPEX.h>

static int fail(const char *message, SPEX_info info)
{
    fprintf(stderr, "%s (SPEX info %d)\n", message, (int) info);
    return 1;
}

int main(int argc, char **argv)
{
    if (argc != 3)
    {
        fprintf(stderr, "usage: %s INPUT OUTPUT\n", argv[0]);
        return 2;
    }
    FILE *input = fopen(argv[1], "r");
    if (input == NULL) return fail("cannot open input", SPEX_INCORRECT_INPUT);
    int64_t n = 0, nnz = 0;
    if (fscanf(input, "%" SCNd64 " %" SCNd64, &n, &nnz) != 2 || n <= 0 || nnz <= 0)
    {
        fclose(input);
        return fail("invalid header", SPEX_INCORRECT_INPUT);
    }

    SPEX_info info = SPEX_initialize();
    if (info != SPEX_OK) return fail("SPEX initialization failed", info);
    SPEX_matrix A = NULL, b = NULL, x = NULL;
    SPEX_options option = NULL;
    info = SPEX_create_default_options(&option);
    if (info != SPEX_OK) return fail("SPEX options failed", info);
    option->algo = SPEX_LU_LEFT;
    option->order = SPEX_COLAMD;
    option->pivot = SPEX_FIRST_NONZERO;

    info = SPEX_matrix_allocate(&A, SPEX_CSC, SPEX_MPZ, n, n, nnz, false, true, option);
    if (info != SPEX_OK) return fail("SPEX matrix allocation failed", info);
    info = SPEX_matrix_allocate(&b, SPEX_DENSE, SPEX_MPZ, n, 1, n, false, true, option);
    if (info != SPEX_OK) return fail("SPEX rhs allocation failed", info);

    for (int64_t k = 0; k <= n; k++)
    {
        if (fscanf(input, "%" SCNd64, &A->p[k]) != 1) return fail("invalid column pointer", SPEX_INCORRECT_INPUT);
    }
    for (int64_t k = 0; k < nnz; k++)
    {
        if (fscanf(input, "%" SCNd64, &A->i[k]) != 1) return fail("invalid row index", SPEX_INCORRECT_INPUT);
    }
    char *token = malloc(1024 * 1024);
    if (token == NULL) return fail("token allocation failed", SPEX_OUT_OF_MEMORY);
    for (int64_t k = 0; k < nnz; k++)
    {
        if (fscanf(input, "%1048575s", token) != 1 || mpz_set_str(A->x.mpz[k], token, 10) != 0)
        {
            return fail("invalid matrix integer", SPEX_INCORRECT_INPUT);
        }
    }
    for (int64_t k = 0; k < n; k++)
    {
        if (fscanf(input, "%1048575s", token) != 1 || mpz_set_str(b->x.mpz[k], token, 10) != 0)
        {
            return fail("invalid rhs integer", SPEX_INCORRECT_INPUT);
        }
    }
    free(token);
    fclose(input);

    info = SPEX_backslash(&x, SPEX_MPQ, A, b, option);
    if (info != SPEX_OK) return fail("SPEX exact solve failed", info);
    FILE *output = fopen(argv[2], "w");
    if (output == NULL) return fail("cannot open output", SPEX_INCORRECT_INPUT);
    for (int64_t k = 0; k < n; k++)
    {
        char *value = mpq_get_str(NULL, 10, x->x.mpq[k]);
        if (value == NULL) return fail("solution conversion failed", SPEX_OUT_OF_MEMORY);
        fprintf(output, "%s\n", value);
        free(value);
    }
    fclose(output);

    SPEX_matrix_free(&x, option);
    SPEX_matrix_free(&b, option);
    SPEX_matrix_free(&A, option);
    free(option);
    SPEX_finalize();
    return 0;
}
