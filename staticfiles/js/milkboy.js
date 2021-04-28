const BASE_URL = location.protocol + "//" + location.host + "/milkboy/stage"
const name = ["UTSUMI", "KOMABA"];
const name2 = ["utsumi", "komaba"];
const pause = sec => new Promise(resolve => setTimeout(resolve, sec * 1000))

var stage = 0;
var need_neta = true;
var rally_num = -2;
var cur_stage_obj = null;
var next = true;

var inputValue = "";
var seed = 0;
var inf = false;

var theme = '？？';
var category = '？？';
var present = '？？';
var father = '？？';
async function showMessage(){
    inputValue = document.getElementById("theme").value;
    stage_max = document.getElementById("length").value;
    inf = document.getElementById("length").checked;
    document.getElementById("neta").style.display = "block";
    document.getElementById("form").style.display = "none";
    await start();
}

async function default_show(){
    document.getElementById("top").style.display = "none";
    document.getElementById("neta").style.display = "block";
    inputValue = '';
    stage_max = 4;
    await start();
}

async function start() {
    await stop();

    theme = '？？';
    category = '？？';
    present = '？？';
    father = '？？';

    await say(0, 'ネタを生成中です。');
    display_message(name2[0], "最大で10秒ほどお待ちください");
    display_message('neta_info', get_neta_info());

    seed = Math.floor( Math.random() * 100000 );
    stage = 0;
    need_neta = true;
    rally_num = -2;
    await pause(0.5);
    await show_next();
}

async function go_top() {
    await stop();
    document.getElementById("top").style.display = "block";
    document.getElementById("neta").style.display = "none";
}

async function go_form() {
    await stop();
    document.getElementById("form").style.display = "block";
    document.getElementById("neta").style.display = "none";
}

function display_message(id, text) {
    document.getElementById(id).innerHTML = text;
    console.log(text);
}

function get_neta_info() {
    return 'お題：' + theme + '　カテゴリー：' + category + '<br>いただいたもの：' + present + '　おとん：' + father;
}

async function say(pearson, text){
    console.log("say_" + name[pearson] + ":" + text);

    display_message(name2[pearson], text);

    const voices = speechSynthesis.getVoices();
    ja_voices = new Array();
    voices.forEach(voice => {
        if(voice.lang.match('ja')) ja_voices.push(voice);
    })

    const uttr = new SpeechSynthesisUtterance(text);
    uttr.voice = ja_voices[pearson];
    speechSynthesis.speak(uttr);

    var i = 0;
    while (speechSynthesis.speaking) {
        await pause(text.length * 0.01);
        i++;
        if (i>=25) {
            speechSynthesis.cancel();
            break;
        }
    }
}

async function tsukami(first_stage){
    // つかみネタ
    await say(0, '整いました');
    await say(0, "どうもーミルクボーイです。お願いします。");
    await say(0, 'あーありがとうございますー。ね、今、' + first_stage["tsukami"] + 'をいただきましたけどもね。');
    present = first_stage["tsukami"];
    display_message('neta_info', get_neta_info());
    await say(0, 'こんなんなんぼあっても良いですからね、ありがたいですよ。いうとりますけどもね。');
    rally_num++;
    if (stage_max == 0) await finish();
    return;
}

async function introduction(first_stage){
    // 導入
    await say(1, 'うちのおかんがね、好きな' + first_stage["category"] + 'があるらしいんやけど、その名前をちょっと忘れたらしくてね。');
    category = first_stage["category"];
    display_message('neta_info', get_neta_info());
    await say(0, 'ほんだら俺がね、おかんの好きな' + first_stage["category"] + '一緒に考えてあげるから、どんな特徴言うてたかとか教えてみてよ。');
    rally_num++;
}

async function print_stage(stage_obj){
    switch (rally_num) {
        case 0:
            // 正しい特徴
            await say(1, stage_obj["featX"]);
            await say(0, stage_obj["featX_reply"]);
            if (stage==0) {
                theme = stage_obj["theme"];
                display_message('neta_info', get_neta_info());
            }
            rally_num++;
            return;

        case 1:
            // 誤った特徴
            await say(1, stage_obj["anti_featX"])
            await say(0, stage_obj["anti_featX_reply"]);
            if (stage_obj["next_is_last"]) {
                stage = -1;
                rally_num = 0;
                need_neta = true;
            }
            else rally_num++
            return;

        case 2:
            // 次のターンへの接続
            await say(0, stage_obj["conjunction"]);
            stage++;
            rally_num = 0;
            need_neta = true;
            return;
  }
}

async function drop(last_stage){
    // 締め
    switch (rally_num) {
        case 0:
            await say(1, last_stage["featX"]);
            await say(0, last_stage["featX_reply"]);
            rally_num++;
            return;

        case 1:
            await say(1, last_stage["anti_featX"]);
            await say(0, last_stage["anti_featX_reply"]);
            father = last_stage["anti_theme"];
            display_message('neta_info', get_neta_info());
            rally_num++;
            return;

        case 2:
            await say(1, last_stage["conjunction"]);
            await say(0, "いや、絶対ちゃうやろ！");
            await say(0, "もうええわ。どうもありがとうございました。");
            stage = -3;
            return;
  }
  return;
}

async function finish() {
    stage = -3;
    await say(0, "もうええわ。どうもありがとうございました。");
}

async function stop() {
    next = false;
    for (var i=0; i<10; i++) {
        speechSynthesis.cancel();
        await pause(0.15);
    }
    for (var i=0; i<2; i++) {
        var div = document.getElementById(name2[i]);
        div.innerHTML = "";
    }
    next = true;
}

async function show_next() {
    if (stage == -3) {
        await say(0, 'このネタが面白かったら下のボタンからシェアをお願いします！');
        if (inf) await showMessage();
        return;
    }

    if (need_neta) {
        getJSON();
        return;
    }

    console.log("=".repeat(50));
    console.log("stage: " + stage + " rally_num: " + rally_num);

    if (rally_num == -2) await tsukami(cur_stage_obj);
    else if (rally_num == -1) await introduction(cur_stage_obj);
    else if (cur_stage_obj["stage"] == -1) await drop(cur_stage_obj);
    else await print_stage(cur_stage_obj);

    if (next) await show_next();
    return;
}

function getJSON() {
    var req = new XMLHttpRequest();           // XMLHttpRequest オブジェクトを生成する
    req.onreadystatechange = function () {    // XMLHttpRequest オブジェクトの状態が変化した際に呼び出されるイベントハンドラ
        if (req.readyState == 4 && req.status == 200) { // サーバーからのレスポンスが完了し、かつ、通信が正常に終了した場合
            cur_stage_obj = JSON.parse(req.responseText);
            console.log(req.responseText);
            // cur_stage_obj = cur_stage_obj[0];
            need_neta = false;
            if (next) show_next();
        }
    };

    console.log(BASE_URL + "?input_theme="+ inputValue +"&stage=" + stage + "&seed=" + seed + "&stage_max=" + stage_max)

    req.open("GET", BASE_URL + "?input_theme=" + inputValue + "&stage=" + stage + "&seed=" + seed+ "&stage_max=" + stage_max, false); // HTTPメソッドとアクセスするサーバーの　URL　を指定
    req.send(null);  // 実際にサーバーへリクエストを送信
}