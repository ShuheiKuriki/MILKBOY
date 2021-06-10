const BASE_URL = location.protocol + "//" + location.host + "/milkboy/"
const name = ["UTSUMI", "KOMABA"];
const name2 = ["utsumi", "komaba"];
const pause = sec => new Promise(resolve => setTimeout(resolve, sec * 1000))

var stage = 0;
var need_neta = true;
var rally_num = -2;
var cur_stage_obj = null;
var next = true;
var request_url = BASE_URL;

var inputValue = "";
var genre = '';
var seed = 0;
var inf = false;
var speed = 1.1;
var vol = 0.6;

var theme = '？？';
var category = '？？';
var present = '？？';
var father = '？？';

async function start_manzai(){
    inputValue = document.getElementById("theme").value;
    stage_max = document.getElementById("length").value;
    inf = document.getElementById("repeat").checked;
    speed = document.getElementById("speed").value;
    vol = document.getElementById("volume").value;
    seed = Math.floor( Math.random() * 100000 );
    document.getElementById("neta_share_button").style.display = "none";
    document.getElementById("skip").style.display = "block";
    document.getElementById("neta").style.display = "block";
    document.getElementById("form").style.display = "none";
    location.href = '#neta';
    await start();
}

async function start_genre(){
    genre = document.getElementById("genre").value;
    stage_max = document.getElementById("length").value;
    inf = document.getElementById("repeat").checked;
    speed = document.getElementById("speed").value;
    vol = document.getElementById("volume").value;
    seed = Math.floor( Math.random() * 100000 );
    document.getElementById("neta_share_button").style.display = "none";
    document.getElementById("skip").style.display = "block";
    document.getElementById("neta").style.display = "block";
    document.getElementById("form").style.display = "none";
    location.href = '#neta';
    await start();
}

async function demo() {
    document.getElementById("neta_share_button").style.display = "none";
    document.getElementById("skip").style.display = "block";
    document.getElementById("top").style.display = "none";
    document.getElementById("neta").style.display = "block";
    document.getElementById("form").style.display = "none";
    document.getElementById("about").style.display = "none";
    location.href = '#neta';
    inputValue = 'カラオケ';
    stage_max = 4;
    seed = 6;
    await start();
}

async function repeat_start() {
    await pause(3);
    if (!next) return;
    seed = Math.floor( Math.random() * 100000 );
    document.getElementById("neta_share_button").style.display = "none";
    document.getElementById("skip").style.display = "block";
    location.href = '#neta';
    await start();
}

async function start() {
    await stop();

    theme = '？？';
    category = '？？';
    present = '？？';
    father = '？？';

    await say(0, 'ネタを生成中です。');
    display_message(name2[0], "10秒ほどお待ちください");
    display_message('neta_info', get_neta_info());

    stage = 0;
    need_neta = true;
    next = true;
    rally_num = -2;
    await pause(0.5);
    await show_next();
}

async function go_top() {
    await stop();
    document.getElementById("top").style.display = "block";
    document.getElementById("about").style.display = "block";
    document.getElementById("neta").style.display = "none";
    document.getElementById("form").style.display = "none";
    location.href = '#top';
}

async function go_form() {
    await stop();
    document.getElementById("form").style.display = "block";
    document.getElementById("neta").style.display = "none";
    document.getElementById("top").style.display = "none";
    document.getElementById("about").style.display = "none";
    location.href = '#form';
}

async function go_about() {
    await stop();
    document.getElementById("form").style.display = "none";
    document.getElementById("neta").style.display = "none";
    document.getElementById("top").style.display = "block";
    document.getElementById("about").style.display = "block";
    location.href = '#about';
}

async function genre_mode() {
    document.getElementById("theme_mode").style.display = "none";
    document.getElementById("genre_mode").style.display = "block";
    location.href = '#form';
}

async function theme_mode() {
    document.getElementById("theme_mode").style.display = "block";
    document.getElementById("genre_mode").style.display = "none";
    location.href = '#form';
}

function display_message(id, text) {
    document.getElementById(id).innerHTML = text;
    console.log(text);
}

function get_neta_info() {
    var res = '';
    if (genre != '') {
        res = 'ジャンル:' + genre + '<br>';
    }
    res += 'いただいたもの：' + present + '<br>カテゴリー：' + category + '<br>お題：' + theme + '<br>おとん：' + father;
    return res;
}

function get_tweet_text() {
    var res = '';
    if (genre != '') {
        res = 'ジャンル: ' + genre + '\n\n';
    }
    res += 'いま「' + present + '」をいただきましたけどもね・・・\n\n';
    res += 'うちのおかんがね、好きな「' + category + '」があるらしいんやけど、その名前を忘れたらしくてね・・・\n\n';
    res += '続きはこちら→'
    return res;
}

function generate_share_button() {
    const baseUrl = 'https://twitter.com/intent/tweet?';
    const text = ['text', get_tweet_text()];
    const hashtags = ['hashtags', ['ミルクボーイ','AI'].join(',')];
    const url = ['url', 'https://www.milkboy-core-ai.tech'];
    const query = new URLSearchParams([text, hashtags, url]).toString();
    const shareUrl = `${baseUrl}${query}`;
    document.getElementById("skip").style.display = 'none';
    var target = document.getElementById("neta_share_button");
    console.log(target.href);
    target.style.display = "block";
    target.href = shareUrl;
    return;
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
    uttr.rate = speed;
    uttr.volume = vol;
    speechSynthesis.speak(uttr);

    var i = 0;
    while (speechSynthesis.speaking) {
        await pause(text.length * 0.01 / speed);
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
    if (!next) return;
    await say(0, "どうもーAIミルクボーイです。お願いします。");
    if (!next) return;

    if (first_stage["tsukami"].length >= 10) {
        var text1 = 'あーありがとうございますー。ね、今、' + first_stage["tsukami"] + 'をいただきましたけどもね。';
        var text2 = 'こんなんなんぼあっても良いですからね、ありがたいですよ。いうとりますけどもね。';
        present = first_stage["tsukami"];
    }
    else {
        var text1 = 'あーありがとうございますー。ね、今、何もいただけませんでしたけどもね。';
        var text2 = '何ももらえなくてもね、聞いてもらえるだけありがたいですよ。いうとりますけどもね。';
        present = '何ももらえませんでした';
    }
    await say(0, text1);
    if (!next) return;
    display_message('neta_info', get_neta_info());
    await say(0, text2);
    rally_num++;
    if (stage_max == 0) await finish();
    return;
}

async function introduction(first_stage){
    // 導入
    if (first_stage["category"] == '') {
        no_manzai();
        return;
    }
    await say(1, 'うちのおかんがね、好きな' + first_stage["category"] + 'があるらしいんやけど、その名前をちょっと忘れたらしくてね。');
    if (!next) return;
    category = first_stage["category"];
    display_message('neta_info', get_neta_info());

    switch (first_stage["pred1"]) {
        case '':
            break;

        default:
            await say(0, '好きな' + first_stage["category"] + '忘れてもうて。どうなってんねんそれ。');
            if (first_stage["pred2"]=='') {
                var preds = first_stage["pred1"];
            }
            else {
                var preds = first_stage["pred1"] + '」か「' + first_stage["pred2"];
            }
            await say(0, 'ほんでもおかんが好きな' + first_stage["category"] + 'なんて、「' + preds + '」くらいでしょう。');
            await say(1, 'それが違うらしいねんな');
    }
    await say(0, 'ほんだら俺がね、おかんの好きな' + first_stage["category"] + '一緒に考えてあげるから、どんな特徴言うてたかとか教えてみてよ。');
    rally_num++;
}

async function no_manzai() {
    await say(1, 'うちのおかんがね、最近はあんまり物忘れをしないらしくてね');
    await say(0, 'ほな、漫才にならんやないかい！');
    finish();
}

async function print_stage(stage_obj){
    switch (rally_num) {
        case 0:
            // 正しい特徴
            await say(1, stage_obj["featX"]);
            if (!next) return;
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
            if (!next) return;
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
            if (!next) return;
            await say(0, last_stage["featX_reply"]);
            rally_num++;
            return;

        case 1:
            await say(1, last_stage["anti_featX"]);
            if (!next) return;
            await say(0, last_stage["anti_featX_reply"]);
            father = last_stage["anti_theme"];
            display_message('neta_info', get_neta_info());
            rally_num++;
            return;

        case 2:
            await say(1, last_stage["conjunction"]);
            if (!next) return;
            await say(0, "いや、絶対ちゃうやろ！");
            if (!next) return;
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
    speechSynthesis.cancel();

    for (var i=0; i<2; i++) {
        var div = document.getElementById(name2[i]);
        div.innerHTML = "";
    }
}

function skip() {
    speechSynthesis.cancel();
    return;
}

async function show_next() {
    if (stage == -3) {
        generate_share_button();
        await say(0, 'このネタが面白かったら下のボタンからシェアをお願いします！');
        if (inf) repeat_start();
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

async function getJSON() {
    var req = new XMLHttpRequest();           // XMLHttpRequest オブジェクトを生成する
    req.onload = function () {    // XMLHttpRequest オブジェクトの状態が変化した際に呼び出されるイベントハンドラ
        if (req.readyState == 4 && req.status == 200) { // サーバーからのレスポンスが完了し、かつ、通信が正常に終了した場合
            cur_stage_obj = JSON.parse(req.responseText);
            console.log(req.responseText);
            // cur_stage_obj = cur_stage_obj[0];
            need_neta = false;
            if (next) show_next();
        }
        else {
            say(0, 'エラーが発生したため、「次のネタ」ボタンを押してやりなおしてください');
        }
    };
    if (genre=='') {
        request_url = BASE_URL + "theme?input_theme="+ inputValue +"&stage=" + stage + "&seed=" + seed + "&stage_max=" + stage_max
    }
    else {
        request_url = BASE_URL + "genre?stage=" + stage + "&seed=" + seed + "&stage_max=" + stage_max + "&genre=" + genre
    }
    console.log(request_url);
    req.open("GET", request_url, true); // HTTPメソッドとアクセスするサーバーの　URL　を指定
    req.send(null);  // 実際にサーバーへリクエストを送信
}