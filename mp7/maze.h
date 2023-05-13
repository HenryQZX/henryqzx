/* Your code here! */
/* Your code here! */
#ifndef _MAZE_H_
#define _MAZE_H_

#include <vector>
#include "cs225/PNG.h"
#include "cs225/HSLAPixel.h"

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
};

#endif