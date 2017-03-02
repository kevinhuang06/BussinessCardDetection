#Description#
    this project can detect a bussiness card in a image.
    
##Usage##
    python ./bizcard.py
 
##Depandence##
    opencv, numpy
##Algorithm Flow##
1. canny edge deteciton
2. find top-3 conturs in edeg-image
3. use houghLine to detection lines
4. divide lines to vertical-set and horizon-set
5. reduce lines by some rules, merge neighbor lines, remove line that Perpendicular to no line
6. find out biggest quadrangle.
7. tell 4 corner point of card
8. generate rectangle card by call affine transformation
