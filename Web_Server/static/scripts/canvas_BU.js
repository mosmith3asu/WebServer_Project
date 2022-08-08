
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
    //actions
    $('.left').click(function(){ if (playing) socket.emit('next_pos', {'action':'left'}) })
    $('.right').click(function(){ if (playing) socket.emit('next_pos', {'action':'right'}) })
    $('.up').click(function(){  if (playing) socket.emit('next_pos', {'action':'up'}) })
    $('.down').click(function(){  if (playing) socket.emit('next_pos', {'action':'down'}) })


/*###################################################################
Handle Response from python server to update game status
###################################################################*/

    socket.on('update_status', (data)=>{
        pos = data['pos']
        finished = data['finished']
        ctx.clearRect(0,0,w,h);
        drawWorld();
        drawPlayers();
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

/*###################################################################
Redraw the world interface
###################################################################*/
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

function drawPlayers() {
    c_player = 'rgba(0,0,255, 1.0)'
    c_partner = 'rgba(100,100,255, 1.0)'
    c_evader = 'rgba(0,255,0, 1.0)'
    sz_player = 0.8
    sz_partner = 0.6
    sz_evader = 0.9

    // EVADER  #############################\
    x = pos[18]*h + (h-sz_evader*h)/2 // row
    y = pos[21]*w + (w-sz_evader*w)/2 // col
    ctx.fillStyle = c_evader //empty
    ctx.fillRect(x, y, sz_evader*w, sz_evader*h)

    // PLAYER #############################\
    x = pos[2]*h + (h-sz_player*h)/2 // row
    y = pos[5]*w + (w-sz_player*w)/2 // col
    ctx.fillStyle = c_player //empty
    ctx.fillRect(x, y, sz_player*w, sz_player*h)

    // Partner #############################\
    x = pos[10]*h + (h-sz_partner*h)/2 // row
    y = pos[13]*w + (w-sz_partner*w)/2 // col
    ctx.fillStyle = c_partner //empty
    ctx.fillRect(x, y, sz_partner*w, sz_partner*h)
}
drawWorld();
drawPlayers();