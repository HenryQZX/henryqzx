/* Your code here! */

#include <vector>
#include "dsets.h"

DisjointSets::DisjointSets(){
    set = {}; //initialize the set to empty
}

//this funtion add n elements (roots) to the set
void DisjointSets::addelements(int num){
    for(int i = 0; i<num; i++){
        set.push_back(-1); //add root node with size 1 (-1)
    }
}

//return the index of the root of the up-tree in which the parameter element resides.
int DisjointSets::find(int elem){
    if(set[elem]<0) return elem; //base case, root if content is negative
    else{
        return find(set[elem]); //recurse to find the next element
    }
}

//union teh set containing elem a and b
//the smaller (in terms of number of nodes) should point at the larger.
void DisjointSets::setunion(int a, int b){
    int root1 = find(a);    //find the root of a
    int root2 = find(b);    //find the root of b
    if(root1 == root2){
        return; //if root1 is root2, just return
    }
    int new_size = size(root1) + size(root2); //get the new size of union set
    
    if(size(root1) <= size(root2)){ //if a is larger or equal
        set[root2] = root1; //connect the b to a
        set[root1] = new_size;  //set size for a
    }
    else{
        set[root1] = root2; //if b is larger
        set[root2] = new_size;  //connect a to b and set new size of b
    }
}

//return the size of the given elem's root's set
int DisjointSets::size(int elem){
    int root = find(elem); //find the root of given elem
    return set[root]; //return the size
}