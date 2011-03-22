clear 
clear all
clc

% variables:
hi = 0.7;
lo = 0.5;
xpos = 200;
ypos = 200;
numC = 1;
mag = 2;

tok1 = 2;
tok2 = 0;
tok3 = 1;

I = imread('Sky.png');

if (tok1 == 1)   
    h = fspecial('motion', 20, 25);
    fI = imfilter(I, h);

elseif (tok1 == 2)
    
    h = fspecial('motion', 20, 25);
    fI = imfilter(I, h);
    
    if (tok2 == 0)
        BW = contrast(lo , hi, fI);
    elseif (tok2 == 1)
        BW = contrast(lo - 0.2 , hi, fI);
    elseif (tok2 == 2)
        BW = contrast(lo , hi + 0.2, fI);
    end
    
end


if (tok3 == 1)
    
    K = zoom(BW,mag, xpos, ypos);
    
    [pos,xy] = democluster(numC,K); 
    
    imshow(K)
    
    RectangleofInterest(pos,1,0,0,size(K))
    
end
    

    