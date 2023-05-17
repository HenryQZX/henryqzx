/* Your code here! */
#include <algorithm>
#include <vector>
#include <queue>
#include <cstdlib>
#include <sys/time.h>
#include <time.h>
#include "maze.h"
#include "dsets.h"

using namespace cs225;

SquareMaze::SquareMaze(){
    _width = 0;
    _height = 0;
    _size = 0;
    grids = {};
    dset = {};
}

void SquareMaze::makeMaze(int width, int height){
    _width = width;
    _height = height;
    _size = _width*_height;
    dset.addelements(_size);

    for(int x = 0; x<_width; x++){
        for(int y = 0; y<_height; y++){
            Grid temp;
            temp.xy = pair<int, int>(x,y);
            grids.push_back(temp);
        }
    }

    for(int x = 0; x<_width; x++){
        for(int y = 0; y<_height; y++){
            int idx = x + y*_width;
            bool finish = false;
            int aloop = 4;
            int direct = rand() % 4;
            while((!finish)&&(aloop!=0)){
                aloop-- ;
                direct = (direct+1) % 4;
                if(direct == 0){
                    if(x==(_width-1)) continue;
                    if(dset.find(idx)==dset.find(idx+1)) continue;
                    dset.setunion(idx, idx+1);
                    setWall(x, y, 0, false);
                }
                else if(direct == 1){
                    if(y==(_height-1)) continue;
                    if(dset.find(idx)==dset.find(idx+_width)) continue;
                    dset.setunion(idx, idx+_width);
                    setWall(x, y, 1, false);
                }
                else if(direct == 2){
                    if(x==0) continue;
                    if(dset.find(idx)==dset.find(idx-1)) continue;
                    dset.setunion(idx, idx-1);
                    setWall(x-1, y, 0, false);
                }
                else if(direct == 3){
                    if(y==0) continue;
                    if(dset.find(idx)==dset.find(idx-_width)) continue;
                    dset.setunion(idx, idx-_width);
                    setWall(x, y-1, 1, false);
                }
                finish = true;
            }
        }
    }
}

bool SquareMaze::canTravel(int x, int y, int dir) const{
    int idx = x+y*_width;
    if(dir==0){
        if((x<_width-1)&&(grids[idx].rightWall==false)) return true;
        else return false;
    }
    if(dir==1){
        if((y<_height-1)&&(grids[idx].downWall==false)) return true;
        else return false;
    }
    if(dir==2){
        if((x>0)&&(grids[idx-1].rightWall==false)) return true;
        else return false;
    }
    if(dir==3){
        if((y>0)&&(grids[idx-_width].downWall==false)) return true;
        else return false;
    }
    else{
        return false;
    }
}

void SquareMaze::setWall(int x, int y, int dir, bool exists){
    int idx = x+y*_width;
    if(dir==0){
        grids[idx].rightWall=exists;
    }
    else if(dir==1){
        grids[idx].downWall=exists;
    }
}

vector<int> SquareMaze::solveMaze(){
    queue<Grid> q;
    q.push(grids[0]);

    while(!q.empty()){
        Grid temp = q.front();
        q.pop();
        if(canTravel(temp.xy.first, temp.xy.second, 0)){
            grids[temp.xy.first+_width*temp.xy.second+1].pred_direct = 0;
            grids[temp.xy.first+_width*temp.xy.second+1].dis_to_begin = temp.dis_to_begin+1;
            q.push(grids[temp.xy.first+_width*temp.xy.second+1]);
        }
        if(canTravel(temp.xy.first, temp.xy.second, 1)){
            grids[temp.xy.first+_width*temp.xy.second+_width].pred_direct = 1;
            grids[temp.xy.first+_width*temp.xy.second+_width].dis_to_begin = temp.dis_to_begin+1;
            q.push(grids[temp.xy.first+_width*temp.xy.second+_width]);
        }
        if(canTravel(temp.xy.first, temp.xy.second, 2)){
            grids[temp.xy.first+_width*temp.xy.second-1].pred_direct = 2;
            grids[temp.xy.first+_width*temp.xy.second-1].dis_to_begin = temp.dis_to_begin+1;
            q.push(grids[temp.xy.first+_width*temp.xy.second-1]);
        }
        if(canTravel(temp.xy.first, temp.xy.second, 3)){    
            grids[temp.xy.first+_width*temp.xy.second-_width].pred_direct = 3;
            grids[temp.xy.first+_width*temp.xy.second-_width].dis_to_begin = temp.dis_to_begin+1;
            q.push(grids[temp.xy.first+_width*temp.xy.second-_width]);
        }
    }

    int max_idx=0;
    int max_dis=0;
    for(int i = 0; i<_width; i++){
        Grid temp = grids[i+_width*(_height-1)];
        if(temp.dis_to_begin>max_dis){
            max_idx = i + _width*(_height-1);
            max_dis = temp.dis_to_begin;
        }
    }

    vector<int> ans_inv;
    int curr_idx = max_idx;
    while(grids[curr_idx].pred_direct!=-1){
        ans_inv.push_back(grids[curr_idx].pred_direct);
        if(grids[curr_idx].pred_direct==0){
            curr_idx = curr_idx-1;
        }
        else if(grids[curr_idx].pred_direct==1){  
            curr_idx = curr_idx-_width;
        }
        else if(grids[curr_idx].pred_direct==2){
            curr_idx = curr_idx+1;
        }
        else if(grids[curr_idx].pred_direct==3){
            curr_idx = curr_idx+_width;
        }
    }

    vector<int> ans;
    while(!ans_inv.empty()){
        int temp_dir = ans_inv.back();
        ans.push_back(temp_dir);
        ans_inv.pop_back();
    }
    return ans;
}

PNG* SquareMaze::drawMaze(){
    HSLAPixel black(0,0,0);
    PNG* ret = new PNG(_width*10+1, _height*10+1);
    for(int x = 0; x<_width; x++){
        for(int y = 0; y<_height; y++){
            if(x==0){
                for(unsigned int i = 0; i<11; i++){
                    *(ret->getPixel(0, y*10+i)) = black;
                }
            }
            if(y==0){
                for(unsigned int i = 0; i<11; i++){
                    if(x==0) continue; //leave an entrance
                    *(ret->getPixel(x*10+i, 0)) = black;
                }
            }
            if(canTravel(x,y,0)==false){
                for(unsigned int i = 0; i<11; i++){
                    *(ret->getPixel((x+1)*10, y*10+i)) = black;
                }
            }
            if(canTravel(x,y,1)==false){
                for(unsigned int i = 0; i<11; i++){
                    *(ret->getPixel(x*10+i, (y+1)*10)) = black;
                }
            }
        }
    }
    return ret;
}

PNG* SquareMaze::drawMazeWithSolution(){
    PNG* ret = new PNG();
    return ret;
}