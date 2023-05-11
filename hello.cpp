#include <stdio.h>
#include <iostream.h>
#include <cmath>
#include <stdlib>
#include <vector>

using namespace std;

int main(){
    vector<int> v = {1,2,3};
    int a = 0;
    int b = 10;
    double c = exp(2);
    for(int i = 0; i<10 ;i++){
        cout << a+i << b-i << endl;
    }
    cout << "hello world" <<endl;
    cout << c << endl;
    for(auto it : v){
        cout << it << endl;
    }
}