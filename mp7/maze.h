/* Your code here! */
/* Your code here! */
#ifndef _MAZE_H_
#define _MAZE_H_

#include <vector>
#include "cs225/PNG.h"
#include "cs225/HSLAPixel.h"
#include "dsets.h"

using namespace cs225;

enum {RIGHT = 0, DOWN = 1, LEFT = 2, UP = 3};
enum {RIGHTWALL = 1, DOWNWALL = 2, BOTHWALLS = 3};
 
class SquareMaze{

    public:
        SquareMaze();
        void makeMaze(int width, int height);
        bool canTravel(int x, int y, int dir) const;
        void setWall(int x, int y, int dir, bool exists);
        vector<int> solveMaze();
        PNG* drawMaze();
        PNG* drawMazeWithSolution();
        
        class Grid{
        public:
            Grid(){
                rightWall = true;
                downWall = true;
                visited = false;
                dis_to_begin = 0;
                pred_direct = -1;
            }
            bool visited;
            bool rightWall;
            bool downWall;
            pair<int, int> xy;
            int dis_to_begin;
            int pred_direct;
        };

    private:
        int _width;
        int _height;
        int _size;
        vector<Grid> grids;
        DisjointSets dset;
};


#endif