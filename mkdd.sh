#! /bin/sh
###
# Dead simple image creation script by Kevin Neely, 2011
###

### Begin
echo "Usage: mkdd.sh img_device destination_path output_filename"
# future: check existence of $3 and quit if not found

dd_type () {
    type "$1" &> /dev/null ;
}

if dd_type dc3dd; then
    echo "creating image with dc3dd"
    dc3dd hash=md5 if=$1 hof=$2$3.dd log=$2$3.log hlog=$2$3.hlog;
else 
    echo "no dc3dd found, defaulting to dd";
    dd if=$1 of=$2$3.dd   
fi

7z a $2$3.dd.7z -mx=9 $2$3.dd;  # future: if no 7z, default to gzip
