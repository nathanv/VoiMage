function box(I,Flag)
 
h = fspecial('motion', 20, 25);
fI = imfilter(I, h);

BW = contrast(0.5, 0.7, fI);

[pos] = democluster(1,BW); 


if strcmp(Flag,'left')

    RectangleofInterest(pos,1,-10,0,size(I)) 

elseif strcmp(Flag,'right')

    RectangleofInterest(pos,1,10,0,size(I)) 

elseif strcmp(Flag,'up')

    RectangleofInterest(pos,1,0,10,size(I)) 

elseif strcmp(Flag,'down')

    RectangleofInterest(pos,1,0,10,size(I)) 

else

    RectangleofInterest(pos,1,0,0,size(I)) 

end
   
    
    

    