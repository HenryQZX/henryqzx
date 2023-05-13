/* Your code here! */
#ifndef _DEST_H_
#define _DEST_H_

#include <vector>

class DisjointSets{
    public:
        DisjointSets(); //constr
        void addelements(int num); //add elem
        int find(int num); //find root
        void setunion(int a, int b); //get union set
        int size(int elem); //return the size of given union
    private:
        std::vector<int> set;
};

#endif