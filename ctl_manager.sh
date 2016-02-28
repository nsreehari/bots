#! /bin/sh

if [ "x$2" = "x" ];  then
    echo Error: No Bot Handle given
    exit 
fi


SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

date

BOTS_CONFIGS="$SCRIPTPATH/.bots"
BOT_HANDLE="$2"
BOT_HANDLE_DIR="$BOTS_CONFIGS/$BOT_HANDLE"
if [ ! -d "$BOT_HANDLE_DIR" ]; then
    echo Error: Bot Not Registered
    exit 
fi

GEVENT_START="`cat $BOT_HANDLE_DIR/.runscript`"
GITPATH="`cat $BOT_HANDLE_DIR/.gitpath`"

OPENERP_HOME=`dirname $GEVENT_START`
GEVENT_PROGRAM=`basename $GEVENT_START`
GEVENT_PROGRAM1=`echo $GEVENT_PROGRAM | sed -e 's/^[a-zA-Z0-9]/[&]/g'`
STOP_FILE="$OPENERP_HOME/.stop_$BOT_HANDLE"

GEVENT_STATUS=""
GEVENT_PID=""
GEVENT_STATUS=""
ERROR=0

is_service_running() {
    GEVENT_PID=`ps ax | awk '/\/'"$GEVENT_PROGRAM1"'/ {print $1}'`
    if [ "x$GEVENT_PID" != "x" ]; then
        RUNNING=1
    else
        RUNNING=0
    fi
    return $RUNNING
}

is_gevent_running() {
    is_service_running "$GEVENT_PROGRAM"
    RUNNING=$?
    if [ $RUNNING -eq 0 ]; then
        GEVENT_STATUS="$GEVENT_PROGRAM not running"
    else
        GEVENT_STATUS="$GEVENT_PROGRAM already running"
    fi
    return $RUNNING
}

start_gevent() {
    test -f $STOP_FILE && echo $STOP_FILE exists: exiting &&exit
    is_gevent_running
    RUNNING=$?
    if [ $RUNNING -eq 1 ]; then
        echo "$0 $ARG: $GEVENT_PROGRAM already running"
        exit
    fi
    if [ `id -u` != 0 ]; then
        /bin/sh -c "((cd $OPENERP_HOME && $GEVENT_START  $BOT_HANDLE_DIR 2>&1) >>/tmp/cron.out ) &"
    else
        su - daemon -s /bin/sh -c "((cd $OPENERP_HOME && $GEVENT_START   $BOT_HANDLE_DIR 2>&1) >/dev/null) &"
    fi
    sleep 4
    is_gevent_running
    RUNNING=$?
    if [ $RUNNING -eq 0 ]; then
        ERROR=1
    fi

    if [ $ERROR -eq 0 ]; then
        echo "$0 $ARG: $GEVENT_PROGRAM started"
        sleep 2
    else
        echo "$0 $ARG: $GEVENT_PROGRAM could not be started"
        ERROR=3
    fi
}

stop_gevent() {
    NO_EXIT_ON_ERROR=$1
    is_gevent_running
    RUNNING=$?
    if [ $RUNNING -eq 0 ]; then
        echo "$0 $ARG: $GEVENT_STATUS"
        if [ "x$NO_EXIT_ON_ERROR" != "xno_exit" ]; then
            exit
        else
            return
        fi
    fi

    kill $GEVENT_PID
    sleep 6

    is_gevent_running
    RUNNING=$?
    if [ $RUNNING -eq 0 ]; then
            echo "$0 $ARG: $GEVENT_PROGRAM stopped"
        else
            echo "$0 $ARG: $GEVENT_PROGRAM could not be stopped"
            ERROR=4
    fi
}

if [ "x$1" = "xstart" ]; then
    start_gevent
elif [ "x$1" = "xup" ]; then
    start_gevent
elif [ "x$1" = "xdown" ]; then
    stop_gevent
elif [ "x$1" = "xstop" ]; then
    stop_gevent
elif [ "x$1" = "xrefresh" ]; then
    cd $BOT_HANDLE_DIR/src
    /usr/bin/git pull
elif [ "x$1" = "xrestart" ]; then
    stop_gevent
    sleep 3
    start_gevent
elif [ "x$1" = "xstatus" ]; then
    is_gevent_running
    echo "$GEVENT_STATUS"
fi

exit $ERROR
