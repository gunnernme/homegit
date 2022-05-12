# stty erase '^H'
sys="$(uname -s)"
typeset -x XTERM=rxvt
typeset -x ED=vi
typeset -x EDITOR=vi
typeset -x FCEDIT=vi
typeset -x HISTSIZE=1500
typeset -x PAGER="less"
typeset -x DBPATH=$HOME/db
typeset -x WINTOCYG="$HOME/shellbin/wintocyg"
profile_version='$Header: /home/eolson/.profile,v 1.19 2007/03/09 16:41:08 eolson Exp eolson $';

v=${profile_version##*,v }
v=${v%% 2006*}

case $sys in
    Darwin*)
	    UNAMEDIR=/usr/bin
	    X11PATH=/usr/X11R6/bin
	    SPPATH=$HOME/darwinbin
	    ;;
    CYG*)
            UNAMEDIR=/usr/bin
	    MRTGDIR=/usr/local/mrtg-2.14/bin
	    X11PATH=/usr/X11R6/bin


	    WINDRIVE=${WINDIR%%:*}:
	    cwindrive="$("$WINTOCYG" "$WINDRIVE")"
	    cwindir="$("$WINTOCYG" "$WINDIR")"
	    typeset -x win32dir="$("$WINTOCYG" "$WINDIR")"
	    typeset -x userdir="$("$WINTOCYG" "$USERPROFILE")"

	    sys32dir="$win32dir"/system32
	    binddir="$win32dir"/system32/dns
	    wbe32dir="$win32dir"/System32/Wbem

	    SPPATH=$sys32dir:"$binddir"/bin:$HOME/cygbin
	    export apachedir="/cygdrive/c/Program Files/Apache Group/Apache"
	    ;;
    SunOS)
	    SPPATH=/usr/sbin:/usr/local/bin:/usr/local/sbin:$HOME/sparcbin:/opt/sfw/bin
	    ;;
    Linux)
	    SPPATH=/usr/sbin:/usr/local/bin:/usr/local/sbin:$HOME/linuxbin:/sbin
	    ;;

    *)
	    SPPATH=
	    ;;
esac

case $0 in
    *bash*) alias whence="type -p"
	    alias r="fc -s"
	    ;;
esac
: ${UNAME:=${uname:=`${UNAMEDIR:-/bin}/uname -n|tr '[A-Z]' '[a-z]'|tr -d '\015'|cut -d. -f1`}}
export UNAME
xpath=$(echo $PATH|sed -e 's/:\.$//')
path=$("$HOME"/perlbin/nicepath "${xpath}:/usr/ccs/bin:/usr/local/bin:$HOME/perlbin:$HOME/shellbin:$HOME/bin:$ATRIA_BIN:$ATRIA_HOME/etc/utils:$SPPATH$X11PATH" 2>/dev/null)
if test -n "$path"
then
    PATH="$path"
else
    echo "nicepath empty for path"
fi

fpath="$HOME/funcbin"
for file in $(cd "$fpath"; /bin/ls)
do
	myfu="$fpath/$file"
	if test -f "$myfu"
	then
	    # echo "  function $myfu" 1>&2
	    . "$myfu"
	fi
done

typeset -x MANPATH=$MANPATH:$HOME/man:/usr/man:/usr/share/man:/usr/X11R6/man:/usr/local/man:

manpath=$("$HOME"/perlbin/nicepath $MANPATH 2>/dev/null)
if test -n "$manpath"
then
    MANPATH="$manpath"
else
    echo "nicepath empty for manpath"
fi
typeset -x MANPAGER='/usr/bin/less -isrR' PAGER=less
typeset -x CDPATH=.:$HOME:
tags=tags
typeset -x EXINIT="set $undo $TAGLEN $REDRAW $WINDOW tags=$tags ai sm sw=${SW:=4} |ab #i #include|ab #d #define"

if [ -z "$uid" ]
then
    if [ "`type -p getuid`" = "" ]
    then
	id=`id|cut -d' ' -f1`
	uid=`expr "$id" : '.*(\([^)]*\))'`
	idno=`expr "$id" : '.*=\(.*\)([^)]*)'`
	gcosf=`grep $idno /etc/passwd|cut -d: -f5`
	gcos1=`echo $gcosf|cut -d, -f1`
	gcos2=`echo $gcosf|cut -d, -f2`
	gcos3=`echo $gcosf|cut -d, -f3`
	case $gcos1 in 
	    U-*)	gcos=$gcos1;;
	esac
	case $gcos2 in 
	    U-*)	gcos=$gcos2;;
	esac
	case $gcos3 in 
	    U-*)	gcos=$gcos3;;
	esac
	if test -n "$gcos"
	then
	    uid=$gcos
	fi
    else
	uid=`getuid`
    fi
    uid=`echo "$uid"|/usr/bin/tr '\134' '/'|sed -e 's,U-,,;s,/,//,g'|/usr/bin/tr '/' '\134'|tr '[A-Z]' '[a-z]'`
fi
#export uid

if [ -z "$gid" ]
then
    if [ "`type -p getgid`" = "" ]
    then
	id=`id|cut -d' ' -f2`
	gid=`expr $id : '.*(\([^)]*\))'`
    else
	gid=`getgid`
    fi
fi
export gid

last=${#UNAME}
let penult=$last-2
#unamabb=`/bin/uname -n|cut -c${penult}-${last}`
unamabb=$UNAME
#PS1="(${unamabb}:${uid}"':${PWD##*/}/) '
pwdb=${PWD##*/}
pwdb=${pwdb%.*}
PS1="${uid}@${unamabb}"':${PWD##*/}/ ' ||

alias pg=less
DISPLAY=$(workip|tr -d '\015'):0
alias axh="DISPLAY=$DISPLAY addxhosts -h"
#alias vi="ENV= /usr/bin/vi"
set -o vi
alias ls="/bin/ls -aFC"

typeset -x DISPLAY=george:0
typeset -x EXINIT="set ai sw=4 expandtab"
if test -d /home/linuxbrew
then
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
fi
