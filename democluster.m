% numC = number of clusters identified by the user
% BW2 is binary image of the section of interest
% pos is position of the cluster. 
% pos can be used to produce a movable ellipse (note the commented portion à
% below)
function [pos] = democluster(numC,BW2)

[H, theta, rho] = hough(BW2);

peaks = houghpeaks(H, numC,...
     'threshold',ceil(0.5*max(H(:))));
 
lines = houghlines(BW2, theta, rho, peaks);

max_len = 0;
for k = 1:length(lines)
    
   xy = [lines(k).point1; lines(k).point2];
   len = norm(lines(k).point1 - lines(k).point2);
     
   if ( len > max_len)
      max_len = len;
      xy_long = xy;
   end
   
end

pos = [xy_long(1,1), xy_long(1,2), xy_long(2,1)-xy_long(1,1), xy_long(2,2) - xy_long(1,2)];

csvwrite('clusterposition.txt',pos)
%%plot(xy_long(:,1),xy_long(:,2),'LineWidth',2,'Color','blue')
%figure, imshow(BW2),

%hold on 
%Ellipse = imellipse(gca,pos);
%pos = wait(Ellipse);






