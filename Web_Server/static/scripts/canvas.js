
c_player = 'rgba(0,0,255, 1.0)'
c_partner = 'rgba(100,100,255, 1.0)'
c_evader = 'rgba(0,255,0, 1.0)'

var can = document.getElementById("canvas");
var ctx = can.getContext("2d");
var w = can.width;
var h = can.height;

ctx.clearRect(0,0,w,h);
nRow = 7;    // default number of rows
nCol = 7;    // default number of columns
w /= nCol;            // width of a block
h /= nRow;            // height of a block
ctx.font = '48px serif';

/*###################################################################
Interacting with the game using JavaScript and Socket.io
###################################################################*/

playing = true
$(document).ready(function(){
    const socket = io();
    drawWorld();
    init_drawPlayers(pos);
    draw_penalty_overlay(0);
    draw_move_counter(20);
    draw_penalty_counter(0);
    draw_timers(-1);

    //actions
    $('.left').click(function(){ if (playing) socket.emit('next_pos', {'action':'left'}) })
    $('.right').click(function(){ if (playing) socket.emit('next_pos', {'action':'right'}) })
    $('.up').click(function(){  if (playing) socket.emit('next_pos', {'action':'up'}) })
    $('.down').click(function(){  if (playing) socket.emit('next_pos', {'action':'down'}) })


/*###################################################################
Handle Response from python server to update game status
###################################################################*/
    socket.on('update_timer', (data)=>{
        draw_timers(data['timer']);
        draw_move_counter(data['moves']);
      })
    socket.on('update_status', (data)=>{
        new_pos = data['pos']
        timer = data['timer']
        moves = data['moves']
        player_pen = data['player_pen']
        finished = data['finished']
        received_penalty = data['received_penalty']


        ctx.clearRect(0,0,can.width,can.height);
        drawWorld();
        drawPlayers(new_pos);
        draw_move_counter(moves);
        draw_penalty_counter(player_pen);
        draw_timers(timer);
        draw_penalty_overlay(received_penalty);
        draw_finished_overlay(finished);

      })

/* ################ DETECTING ARROW KEYPRESS ################ */
    $(document).keydown(function(e) {
            if (e.keyCode == 37) {
                if (playing) socket.emit('next_pos', {'action':'left'})
            } else if (e.keyCode == 38) {
                //up
                if (playing) socket.emit('next_pos', {'action':'up'})
            } else if (e.keyCode == 39) {
                //right
                if (playing) socket.emit('next_pos', {'action':'right'})
            } else if (e.keyCode == 40) {
                //down
                if (playing) socket.emit('next_pos', {'action':'down'})
            }
        })
    })

///*###################################################################
//Redraw the world interface
//###################################################################*/
function drawWorld() {
    var world_data = [
    [1,1,1,1,1,1,1],
    [1,0,0,0,0,0,1],
    [1,0,1,0,1,0,1],
    [1,0,0,0,0,0,1],
    [1,0,1,0,1,0,1],
    [1,0,0,0,0,0,1],
    [1,1,1,1,1,1,1]];

    c_black = 'rgba(0,0,0, 1.0)'
    c_red = 'rgba(255,0,0, 0.3)'
    c_white ='rgba(255,255,255, 1.0)'
    scale= 1.01

//  LOAD WORLD DATA INTO ARRAY ###########
    var e = 0;
    for (var i = 0; i < world.length; i++) {
        is_num =(world[i]==0 || world[i]==1 || world[i]==2)
        if (is_num && world[i]!=" "){
            r = Math.floor(e/nCol);
            c = e % nCol;
            world_data[r][c] = world[i];
            e += 1
        }
    }

// DRAW ARRAY ###########################
    for (var i = 0; i < nRow; i++) {
        for (var j = 0, col = nCol; j <= col; j++) {
            val = world_data[i][j]
//            if (val==0){
//                ctx.fillStyle = c_white //empty
//                ctx.fillRect(j * w, i * h, scale*w, scale*h)
            if (val==1){
                ctx.fillStyle = c_black //border
                ctx.fillRect(j * w, i * h, scale*w, scale*h)
            } else if (val==2){
                ctx.fillStyle = c_red //penalty
                ctx.fillRect(j * w, i * h, scale*w, scale*h)
            }
        }
    }
}

function init_drawPlayers(loc) {
    c_player = 'rgba(0,0,255, 1.0)'
    c_partner = 'rgba(100,100,255, 1.0)'
    c_evader = 'rgba(0,255,0, 1.0)'
    sz_player = 0.8
    sz_partner = 0.6
    sz_evader = 0.9

    // EVADER  #############################\
    x = loc[18]*h + (h-sz_evader*h)/2 // row
    y = loc[21]*w + (w-sz_evader*w)/2 // col
    ctx.fillStyle = c_evader //empty
    ctx.fillRect(x, y, sz_evader*w, sz_evader*h)

    // PLAYER #############################\
    x = loc[2]*h + (h-sz_player*h)/2 // row
    y = loc[5]*w + (w-sz_player*w)/2 // col
    ctx.fillStyle = c_player //empty
    ctx.fillRect(x, y, sz_player*w, sz_player*h)

    // Partner #############################\
    x = loc[10]*h + (h-sz_partner*h)/2 // row
    y = loc[13]*w + (w-sz_partner*w)/2 // col
    ctx.fillStyle = c_partner //empty
    ctx.fillRect(x, y, sz_partner*w, sz_partner*h)
}
function drawPlayers(loc) {
    iplayer     = 0
    irobot      = 1
    ievader     = 2
    ix = 1
    iy = 0

//    c_player = 'rgba(0,0,255, 1.0)'
//    c_partner = 'rgba(100,100,255, 1.0)'
//    c_evader = 'rgba(0,255,0, 1.0)'
    sz_player = 0.8
    sz_partner = 0.6
    sz_evader = 0.9

    // EVADER  #############################\
    x = loc[ievader][iy]*h + (h-sz_evader*h)/2 // row
    y = loc[ievader][ix]*w + (w-sz_evader*w)/2 // col
    ctx.fillStyle = c_evader //empty
    ctx.fillRect(x, y, sz_evader*w, sz_evader*h)

    // PLAYER #############################\
    x = loc[iplayer][iy]*h + (h-sz_player*h)/2 // row
    y = loc[iplayer][ix]*w + (w-sz_player*w)/2 // col
    ctx.fillStyle = c_player //empty
    ctx.fillRect(x, y, sz_player*w, sz_player*h)

    // Partner #############################\
    x = loc[irobot][iy]*h + (h-sz_partner*h)/2 // row
    y = loc[irobot][ix]*w + (w-sz_partner*w)/2 // col
    ctx.fillStyle = c_partner //empty
    ctx.fillRect(x, y, sz_partner*w, sz_partner*h)
}

function draw_finished_overlay(is_finished){
    if (is_finished){
        c_overlay = 'rgba(0,0,0,0.2)';
        c_text = 'rgba(255,255,255,1.0)';
        ctx.fillStyle = c_overlay;
        ctx.fillRect(0, 0, can.width, can.height);

        ctx.font = '48px serif';
        ctx.textAlign = 'center';
        ctx.fillStyle = c_text;
        ctx.fillText('Game',    350, 300);
        ctx.fillText('Complete',350, 350);
    }
 }
function draw_penalty_overlay(is_pen){
    if (is_pen){
        c_overlay = 'rgba(255,0,0,0.2)';

        ctx.fillStyle = c_overlay;
        ctx.fillRect(0, 0, can.width, can.height);
    }
 }

 function draw_penalty_counter(nPen){
    yloc = 662
    c_text = 'rgba(200,0,0,1.0)';
    ctx.font = '30px serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = c_text;
    ctx.fillText('Penalty: ',  300, yloc);
    ctx.fillText(nPen, 375, yloc);
 }

 function draw_move_counter(nMoves){
    yloc = 62
    xlabel = 300
    xcounter = 375
    h_patch = 90

    c_text = 'rgba(255,255,255,1.0)';
    c_bg = 'rgba(0,0,0,1.0)';
//    c_bg = 'rgba(255,255,0,1.0)';

    // Clear counter area
    ctx.fillStyle = c_bg;
    ctx.clearRect(0,0,can.width,h_patch)
    ctx.fillRect(0,0,can.width,h_patch)

    // Add counter elements in
    ctx.font = '30px serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = c_text;
    ctx.fillText('Moves: ',  xlabel, yloc);
    ctx.fillText(nMoves, xcounter, yloc);

    //ctx.fillRect(0, 0, can.width, can.height);

 }

 function draw_timers(timer_val){
    y_start = 100
    y_end = 600
    timer_height = y_end-y_start
    timer_width = 60
    x_evader = 50
    x_player = 650
    c_fill =  'rgba(0,0,0, 1.0)'
    c_player_dim = 'rgba(0,0,150, 1.0)'
    c_evader_dim = 'rgba(0,150,0, 1.0)'

    // Clear timer space
    ctx.clearRect(x_evader-timer_width/2, y_start, timer_width, timer_height)
    ctx.clearRect(x_player-timer_width/2, y_start, timer_width, timer_height)
    ctx.fillStyle = c_fill //empty
    ctx.fillRect(x_evader-timer_width/2, y_start, timer_width, timer_height)
    ctx.fillRect(x_player-timer_width/2, y_start, timer_width, timer_height)

    if (timer_val<=0){
        prog = (1+timer_val)*timer_height
        tHeight =y_start+prog

        // Evader Timer --------------------------
        ctx.fillStyle = c_evader //empty
        ctx.fillRect(x_evader-timer_width/2, tHeight, timer_width, y_end-tHeight)

        // Disabled player timer -----------------
        ctx.fillStyle = c_player_dim
        ctx.fillRect(x_player-timer_width/2, y_start, timer_width, timer_height)

    }else{
        prog = timer_val*timer_height
        tHeight = y_start+prog

        // player timer --------------------------
        ctx.fillStyle = c_player
        ctx.fillRect(x_player-timer_width/2, tHeight, timer_width, y_end-tHeight)

        // Disabled Evader Timer -----------------
        ctx.fillStyle = c_evader_dim //empty
        ctx.fillRect(x_evader-timer_width/2, y_start, timer_width,timer_height)
    }
 }