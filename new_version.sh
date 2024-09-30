#Build with poetry an sum new version
#merm_orquestrador-0.1.0-py3-none-any --> merm_orquestrador-0.1.1-py3-none-any na pasta dist
#build and sum version number in ./dist/version.txt
lambda_name="myNumberFunction"
packege_name=""

rm -rf $lambda_name
mkdir $lambda_name

#Get current version in txt file and sum 1
current_version=$(cat ./dist/version.txt)
new_version=$(echo $current_version | awk -F. '{$NF = $NF + 1;} 1' | sed 's/ /./g')

#Replace version in txt file
echo $new_version > ./dist/version.txt

poetry build

# #set name of file *.whl with version with new version
 mv ./dist/$packege_name-$current_version-py3-none-any.whl ./dist/$packege_name-$new_version-py3-none-any.whl

#remove old version
rm ./dist/$packege_name-0.1.0-py3-none-any.whl
rm ./dist/$packege_name-0.1.0.tar.gz



#generate requirements.txt
poetry export --without-hashes -f requirements.txt > requirements.txt
mv requirements.txt $lambda_name
cd $lambda_name
pip install --upgrade --target . -r requirements.txt

#copy files importants .py and packege
cp ../index.py .
cp ../types_inputs.py .
cp ../test.py .
cp -r ../$packege_name .
##########################################

#zip all files compression 9
cd ..
zip  -r -9  $lambda_name.zip ./$lambda_name