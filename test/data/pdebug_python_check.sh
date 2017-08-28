#!/bin/bash
#pdebug_python_CMS.sh ../physics_cms.txt $HEPPY/data/required_cms_physics.txt
FILE="compare.out"
if [ -f $FILE ]
then
rm $FILE
fi
if [ ! $# == 2 ]
then
 echo "Usage: pdebug_python.sh input file compare file"
 return 1
fi

PHYSICS=$1 #"physics_cms.txt"
MATCHPHYSICS=$2 #$HEPPY/data/required_cms_physics.txt

if ([ -f $PHYSICS ] && [ -f $MATCHPHYSICS ])
then

diff $MATCHPHYSICS $PHYSICS  >  $FILE

if [ -f $FILE ]
then
if [[ -s $FILE ]];
then
echo "$FILE is different"
return 1
else
echo "$FILE matches"
return 0
#rm $FILE

fi
else
echo "$FILE not found."
fi
else
echo "$PHYSICS or $MATCHPHYSICS not found."
fi
return 1
