#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <inttypes.h>

#define HASH_SIZE  100003  // A prime number for the hash table size (somewhat arbitrary)

/*
  We will store each word's frequency in a linked list (simple approach).
  For more advanced usage, you might store them in a balanced tree or
  a dynamic data structure. But a basic hash map with separate chaining
  is sufficient to demonstrate the method.
*/

typedef struct WordFreq {
    char *word;               // dynamically allocated copy of the word
    int   count;              // how many times it appears
    struct WordFreq *next;    // next in the collision chain
} WordFreq;

/* Global or local function prototypes. */
static unsigned hash_function(const char *word);
static WordFreq* lookup_or_insert(WordFreq **table, const char *word);
static char** build_top_n(WordFreq **table, int n, int *actual_count);
static void free_table(WordFreq **table);

char **find_frequent_words(const char *path, int32_t n)
{
    /*
        1) Open the file for reading.
        2) Create a hash table array of WordFreq* of size HASH_SIZE, initialized to NULL.
        3) Read lines, tokenize, and update frequency counts in the hash table.
        4) Build a sorted list of words by frequency.
        5) Extract top n.
        6) Return them as a char**.
    */

    // -------------------
    // 1) Open the file
    // -------------------
    FILE *fp = fopen(path, "r");
    if (!fp) {
        fprintf(stderr, "Error: Could not open file '%s'.\n", path);
        return NULL;
    }

    // ----------------------------
    // 2) Create the hash table
    // ----------------------------
    WordFreq *table[HASH_SIZE];
    for (int i = 0; i < HASH_SIZE; i++) {
        table[i] = NULL;
    }

    // -----------------------------------
    // 3) Read and tokenize line by line
    // -----------------------------------
    // We will read each line, then parse out words by scanning
    // for a-z or A-Z characters, splitting on anything else.

    char buffer[4096];
    while (fgets(buffer, sizeof(buffer), fp)) {
        // We'll parse the line character by character
        // and isolate sequences of letters as words.
        int len = (int)strlen(buffer);
        int start_idx = -1; // marker for the start of a word, -1 means "not currently in a word"

        for (int i = 0; i <= len; i++) {
            char c = buffer[i];
            // Check if it's an alphabetic char (a-z, A-Z) or end-of-line
            if (isalpha((unsigned char)c)) {
                // If we aren't in a word yet, mark start
                if (start_idx < 0) {
                    start_idx = i;
                }
            } else {
                // We hit a non-alpha or end of line => if we were in a word, end it
                if (start_idx >= 0) {
                    int word_length = i - start_idx;
                    if (word_length > 0) {
                        // Extract the word substring
                        char temp[512]; // temporary buffer for the word
                        if (word_length >= (int)sizeof(temp)) {
                            // Just skip if word is too big for this example
                            start_idx = -1;
                            continue;
                        }
                        memcpy(temp, &buffer[start_idx], word_length);
                        temp[word_length] = '\0';

                        // Convert to lowercase
                        for (int k = 0; k < word_length; k++) {
                            temp[k] = (char)tolower((unsigned char)temp[k]);
                        }

                        // Insert/lookup in hash table
                        WordFreq *wf = lookup_or_insert(table, temp);
                        wf->count += 1;
                    }
                    // Reset for next word
                    start_idx = -1;
                }
            }
        }
    }

    fclose(fp);

    // ----------------------------------
    // 4) Build array sorted by frequency
    // 5) Extract top n
    // ----------------------------------
    int actual_count = 0;  // how many distinct words we found
    char **top_words = build_top_n(table, n, &actual_count);

    // --------------------------
    // 6) Clean up hash table
    // --------------------------
    free_table(table);

    // Return the top words (char**). The caller can use them,
    // but should eventually free them if it wants to avoid leaks.
    // We'll have allocated top_words array and each string inside it.
    return top_words;
}

/* ----------------------------------------------------------------------
   Hash function (simple djb2-like or similar).
   ---------------------------------------------------------------------- */
static unsigned hash_function(const char *word)
{
    // A common simple string hash approach
    unsigned hash = 5381;
    while (*word) {
        // (hash << 5) + hash = hash * 33
        hash = ((hash << 5) + hash) + (unsigned char)(*word);
        word++;
    }
    return hash % HASH_SIZE;
}

/* ----------------------------------------------------------------------
   lookup_or_insert: If 'word' is already in the table, return pointer
   to its WordFreq record. Otherwise, insert it with count=0 and return it.
   ---------------------------------------------------------------------- */
static WordFreq* lookup_or_insert(WordFreq **table, const char *word)
{
    unsigned h = hash_function(word);
    WordFreq *cur = table[h];
    while (cur) {
        if (strcmp(cur->word, word) == 0) {
            return cur; // found
        }
        cur = cur->next;
    }
    // Not found, create a new entry
    WordFreq *new_node = (WordFreq*)malloc(sizeof(WordFreq));
    new_node->count = 0;
    new_node->word = (char*)malloc(strlen(word) + 1);
    strcpy(new_node->word, word);
    new_node->next = table[h];
    table[h] = new_node;
    return new_node;
}

/* ----------------------------------------------------------------------
   build_top_n: Gather all (word, freq) pairs from the table into
   a dynamic array, sort it, and return the top n words as char**.
   *actual_count returns how many distinct words were found.
   ---------------------------------------------------------------------- */
static char** build_top_n(WordFreq **table, int n, int *actual_count)
{
    // First, collect all (word, freq) into a dynamic array
    int capacity = 10000; // initial guess, will expand if needed
    int size = 0;
    // We'll store pointers to WordFreq in an array
    WordFreq **arr = (WordFreq**)malloc(capacity * sizeof(WordFreq*));

    // Traverse the hash table
    for (int i = 0; i < HASH_SIZE; i++) {
        WordFreq *cur = table[i];
        while (cur) {
            if (size >= capacity) {
                // expand
                capacity *= 2;
                arr = (WordFreq**)realloc(arr, capacity * sizeof(WordFreq*));
            }
            arr[size++] = cur;
            cur = cur->next;
        }
    }

    *actual_count = size; // total distinct words

    // Sort by frequency (descending). If you want a secondary tiebreak (alphabetical),
    // you can incorporate that as well.
    // We'll do a simple qsort with a comparison function.
    qsort(arr, size, sizeof(WordFreq*), 
          [](const void *a, const void *b) {
              WordFreq *wa = *(WordFreq**)a;
              WordFreq *wb = *(WordFreq**)b;
              // descending freq
              return (wb->count - wa->count);
          }
    );

    // Now, pick the top n (or fewer if size < n)
    int take_count = (n < size) ? n : size;

    // Allocate the output array of strings
    char **result = (char**)malloc((take_count + 1) * sizeof(char*));
    // We'll store them as brand-new copies so that we can free the entire hash table later
    for (int i = 0; i < take_count; i++) {
        // copy the word
        const char *src = arr[i]->word;
        result[i] = (char*)malloc(strlen(src) + 1);
        strcpy(result[i], src);
    }
    // Null-terminate the array in case the caller wants to treat it as a list
    result[take_count] = NULL;

    free(arr);
    return result;
}

/* ----------------------------------------------------------------------
   free_table: free all linked lists in the hash table.
   (Does not free the final 'top_words' array we return.)
   ---------------------------------------------------------------------- */
static void free_table(WordFreq **table)
{
    for (int i = 0; i < HASH_SIZE; i++) {
        WordFreq *cur = table[i];
        while (cur) {
            WordFreq *tmp = cur;
            cur = cur->next;
            free(tmp->word);
            free(tmp);
        }
        table[i] = NULL;
    }
}
