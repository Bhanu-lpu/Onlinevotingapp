#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char *data;
    char candidate[100];

    printf("Content-Type: text/html\n\n");

    data = getenv("CONTENT_LENGTH");

    int len = 0;
    if (data != NULL) len = atoi(data);

    char input[200];
    fread(input, 1, len, stdin);
    
    // Extract vote (value after candidate=)
    sscanf(input, "candidate=%s", candidate);

    // URL decoding for NOTA and special characters (basic decode for spaces or %20)
    for (int i = 0; candidate[i]; i++) {
        if (candidate[i] == '+') candidate[i] = ' ';
    }

    // Save vote to file
    FILE *file = fopen("/usr/lib/cgi-bin/votes.txt", "a");
    if (file == NULL) {
        printf("<html><body><h1>Error saving vote.</h1></body></html>");
        return 1;
    }
    fprintf(file, "%s\n", candidate);
    fclose(file);

    // Display thank you message
    printf("<html><body style='font-family: Arial; text-align: center; margin-top: 50px;'>");
    printf("<h1>✅ Thank you for voting!</h1>");
    printf("<p>You voted for: <strong>%s</strong></p>", candidate);
    printf("<a href='/index.html' style='display:inline-block;margin-top:20px;padding:10px 20px;background:#2b2d42;color:white;text-decoration:none;border-radius:5px;'>Back to Voting</a>");
    printf("</body></html>");

    return 0;
}
