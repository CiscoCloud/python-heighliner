#!/bin/bash
## Author : Amulya Sharma

# This script assumes you don't have a source in tarball formant, and that
# one should always be created for you.

echo " input to script $1 $2 $3 $4 $5 $6"
usage ()
{
  echo "Usage :$0  -n name -s source -sfile specfile -b <build_number> -mock"
  echo "Example: $0 -n helloworld -s  src -sfile hello.spec -b 13 -mock"
  exit
}
# TODO : Do better implementation of passing parameters
if [ $# -lt  4 ] ; then
  echo $#
  usage
fi
BUILDNUM_COMMAND2=" no_build_number true"
MOCK=0
while [ "$1" != "" ]; do
case $1 in
        -s )           shift
                       SOURCE=$1
                       ;;
        -n )           shift
                       NAME=$1
                       ;;
        -sfile )      shift
                       SPECFILE=$1
                       ;;
        -ppath )       shift
                       PATCHES_PATH=$1
                       ;;
        -mock )        MOCK=1
                       ;;
        -b )           shift
                       BUILDNUM=$1
                       BUILDNUM_COMMAND2=" build_number ."
                       ;;
         * )           QUERY=$1
    esac
    shift
done

# extra validation
[ "$SPECFILE" = "" ] && usage
[ "$NAME" = "" ] && usage

SAVEDIR=$PWD
cd ./${SOURCE}
test -v BUILDNUM || BUILDNUM_COMMAND2=" build_number ."

if [[ -n $GERRIT_BRANCH ]]; then
  BRANCHNAME=$(echo $GERRIT_BRANCH | tr /_\- .)
else
  # This will always return HEAD when we are in a detached head state
  BRANCHNAME=`git rev-parse --abbrev-ref HEAD`
fi

if [[ "$BRANCHNAME" == "HEAD" ]] || [[ "$BRANCHNAME" == "master" ]]; then
  BRANCHNAME=''
  RPM_BRANCHNAME=''
else
  RPM_BRANCHNAME=".${BRANCHNAME}"
fi

# if [[ -n $GERRIT_CHANGE_NUMBER ]] && [[ $USE_GERRIT_BUILDNUM ]]; then
#   BUILDNUM="${GERRIT_CHANGE_NUMBER}.${GERRIT_PATCHSET_NUMBER}"
# else:
BUILDNUM=`git rev-list HEAD --count`
# fi

cd $SAVEDIR
echo $BUILDNUM_COMMAND2

## We need to inspect the source directory to see
## if there is a valid upstream tarball. If there is we
## should not be creating the tarball.

## Creating a Source RPM for $SOURCE
echo "--------------------------------------------------"
echo "Start Creating SOURCE RPM for" $SOURCE
echo "--------------------------------------------------"
## Create Build Area
        BASE_DIR=$PWD
        BUILD_DIR=${NAME}_build
        rm -rf ./$BUILD_DIR
        mkdir -p ./$BUILD_DIR/{SPECS,SOURCES,RPMS,SRPMS,BUILDROOT}

## Copy Spec file to build area
cp $SPECFILE ./$BUILD_DIR/SPECS/

## Check the Sources within the spec file to See if we have a tarball that
## matches. if we do, use it directly instead of trying to create a new one.
##
## TODO: be aware that this only supports a single source tar ball..RPMS can
##       have multiple sources.
source_version=$(grep "Version:" $SPECFILE | awk '{print $2}')
echo $source_version
source_tarball=$(egrep "Source[0-9]*\:\s*${NAME}-${source_version}.tar.gz" ${SPECFILE} | awk '{print $2}' | head -n1)
echo $source_tarball

if [[ "$source_tarball" != "" ]] && [[ -a "${SOURCE}/${source_tarball}" ]]
then
  echo "--------------------------------------------------"
  echo "Copy Source tarball into SOURCES: " $source_tarball
  echo "--------------------------------------------------"
  cp ./$SOURCE/$source_tarball ./$BUILD_DIR/SOURCES/
else
  echo "--------------------------------------------------"
  echo "Create Source tarball: " $SOURCE
  echo "--------------------------------------------------"
  ##Copy all Source to Build area, source and patches

  ##Copy all patches
  if [ "$PATCHES_PATH" != "" ]
  then
     cp -r ./$PATCHES_PATH/* ./$BUILD_DIR/SOURCES/
  fi

  if [ -z "$SOURCE" ]; then
    git archive -o ./$BUILD_DIR/SOURCES/$NAME.tar.gz --prefix="$NAME/" HEAD
  else
    cp -r ./$SOURCE ./$BUILD_DIR/SOURCES/

    find ./$BUILD_DIR/SOURCES

    # Delete git metadata folder
    find ./$BUILD_DIR/SOURCES | grep .git | xargs rm -rf

    cd ./$BUILD_DIR/SOURCES/
    SOURCE_BASE=`basename $SOURCE`
    tar -czf ./$NAME.tar.gz ./$SOURCE_BASE
    cd ../../
  fi
fi


echo "--------------------------------------------------"
echo "run RPM Build"
echo "--------------------------------------------------"

rpmbuild -D '_topdir '"$BASE_DIR/$BUILD_DIR" -D '_tmppath /tmp' -D "${BUILDNUM_COMMAND2}${BUILDNUM}" -D "branch_name ${RPM_BRANCHNAME}" -bs ./$SPECFILE
OUT=$?
if [ $OUT -eq 0 ];then
   echo "srpm build completed successfully "
else
   echo "Problem with srpm build"
   exit 1
fi
rm -rf  ./$BUILD_DIR/{SPECS,SOURCES,RPMS,BUILDROOT}
ls ./${BUILD_DIR}/

pwd
SRPM_FILE=`ls $PWD/${BUILD_DIR}/SRPMS/*.src.rpm`
echo "SRPM is :" $SRPM_FILE

if [ -f ${SRPM_FILE} ]
then
    echo "generating rpm for"
    echo "---------------------"
    echo "Got SRPM as " ./${SRPM_FILE}
    echo "mock $MOCK"
    if [ $MOCK -eq 1 ]; then
        sudo mock --resultdir "$BASE_DIR/$BUILD_DIR/RPMS" -D "${BUILDNUM_COMMAND2}${BUILDNUM}" -D "branch_name ${RPM_BRANCHNAME}" ${SRPM_FILE}
    else
        rpmbuild -D '_topdir '"$BASE_DIR/$BUILD_DIR" -D '_tmppath /tmp' -D "${BUILDNUM_COMMAND2}${BUILDNUM}" -D "branch_name ${RPM_BRANCHNAME}" --rebuild ${SRPM_FILE}
    fi
    OUT=$?
    if [ $OUT -eq 0 ];then
       echo "rpm build completed successfully "
       exit 0
    else
       echo "Problem with srpm build"
       exit 1
    fi
else
    echo "no SRPM"
    exit 3
fi
