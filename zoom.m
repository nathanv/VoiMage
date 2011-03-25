function [ZI] = zoom (I,Flag)

N = I;
I = imread(I);

if strcmp(Flag,'more')
    
    magnify(I,N, 3, 0, 0);
    
elseif strcmp(Flag,'left')
    
    magnify(I,N,2, -25, 0);
    
elseif strcmp(Flag,'right')
    
    magnify(I,N,2, 25, 0);
    
elseif strcmp(Flag,'up')
    
    magnify(I,N,2, 0, 25);
    
elseif strcmp(Flag,'down')

    magnify(I,N,2, 0, -25);  
    
else
    
    magnify(I,N,2, 0, 0);  
    
end