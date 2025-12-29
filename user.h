#ifndef USER_H
#define USER_H

#define MAX_NAME 50

typedef struct User {
    int user_id;
    char name[MAX_NAME];
    int age;
    int ratings_count;
    float avg_rating_given;
} User;

User* create_user(int id, const char* name, int age);
void print_user(User* user);

#endif
