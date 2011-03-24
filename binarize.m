function binarize (I, Flag)

h = fspecial('motion', 20, 25);
fI = imfilter(I, h);

hi = 0.7;
lo = 0.5;

if strcmp(Flag, 'high')
    contrast(lo , hi + 0.2, fI);
elseif strcmp(Flag, 'low')
    contrast(lo - 0.2 , hi, fI);
else
    contrast(lo , hi, fI);
end