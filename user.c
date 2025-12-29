#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "user.h"

User* create_user(int id, const char* name, int age) {
    User* user = (User*)malloc(sizeof(User));
    user->user_id = id;
    strncpy(user->name, name, MAX_NAME - 1);
    user->name[MAX_NAME - 1] = '\0';
    user->age = age;
    user->ratings_count = 0;
    user->avg_rating_given = 0.0;
    return user;
}

void print_user(User* user) {
    printf("User ID: %d\n", user->user_id);
    printf("Name: %s\n", user->name);
    printf("Age: %d\n", user->age);
    printf("Ratings Given: %d\n", user->ratings_count);
    printf("Average Rating Given: %.2f\n", user->avg_rating_given);
}
