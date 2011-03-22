% IJ : Image. mag: magnification factor. xpos: origin x coordinate
% ypos : origin y coordinate

function[Z] = zoom(image,mag, xpos, ypos)
IJ = imread(image);
hFig = figure('Toolbar','none','Menubar','none');
hIm = imshow(IJ);

hSP = imscrollpanel(hFig,hIm);

hMagBox = immagbox(hFig,hIm);
pos = get(hMagBox,'Position');
set(hMagBox,'Position',[0 0 pos(3) pos(4)])

apiSP = iptgetapi(hSP);
apiSP.setMagnification(mag)

api.setVisibleLocation(xpos, ypos)

r = apiSP.getVisibleImageRect();
rr = round(r); 

Z = IJ(rr(2):rr(2)+rr(4),rr(1):rr(1) + rr(3));
  
%imshow(Z)
