const BASE_URL = location.protocol + "//" + location.host + "/milkboy/"
const NAMES = ["UTSUMI", "KOMABA"];
const SMALL_NAMES = ["utsumi", "komaba"];
const PAUSE = sec => new Promise(resolve => setTimeout(resolve, sec * 1000))

var STAGE = 0;
var STAGE_MAX = 4;
var NEED_STORY = true;
var RALLY_NUM = -2;
var CUR_STAGE_OBJ = null;
var NEXT = true;

var INPUT_VALUE = "";
var GENRE = '';
var SEED = 0;
var INF = false;
var SPEED = 1.1;
var VOL = 0.6;

var THEME = '？？';
var CATEGORY = '？？';
var PRESENT = '？？';
var FATHER = '？？';

async function start_story(){
    INPUT_VALUE = document.getElementById("theme").value;
    STAGE_MAX = document.getElementById("length").value;
    INF = document.getElementById("repeat").checked;
    SPEED = document.getElementById("speed").value;
    VOL = document.getElementById("volume").value;
    SEED = Math.floor( Math.random() * 100000 );
    document.getElementById("story_share_button").style.display = "none";
    document.getElementById("skip").style.display = "block";
    document.getElementById("story").style.display = "block";
    document.getElementById("form").style.display = "none";
    location.href = '#story';
    await start();
}

async function start_genre(){
    GENRE = document.getElementById("genre").value;
    STAGE_MAX = document.getElementById("length").value;
    INF = document.getElementById("repeat").checked;
    SPEED = document.getElementById("speed").value;
    VOL = document.getElementById("volume").value;
    SEED = Math.floor( Math.random() * 100000 );
    document.getElementById("story_share_button").style.display = "none";
    document.getElementById("skip").style.display = "block";
    document.getElementById("story").style.display = "block";
    document.getElementById("form").style.display = "none";
    location.href = '#story';
    await start();
}

async function demo() {
    document.getElementById("story_share_button").style.display = "none";
    document.getElementById("skip").style.display = "block";
    document.getElementById("top").style.display = "none";
    document.getElementById("story").style.display = "block";
    document.getElementById("form").style.display = "none";
    document.getElementById("about").style.display = "none";
    location.href = '#story';
    INPUT_VALUE = 'カラオケ';
    STAGE_MAX = 4;
    SEED = 0;
    await start();
}

async function repeat_start() {
    await PAUSE(3);
    if (!NEXT) return;
    SEED = Math.floor( Math.random() * 100000 );
    document.getElementById("story_share_button").style.display = "none";
    document.getElementById("skip").style.display = "block";
    location.href = '#story';
    await start();
}

async function start() {
    await stop();

    THEME = '？？';
    CATEGORY = '？？';
    PRESENT = '？？';
    FATHER = '？？';

    await say(0, 'ネタを作っています。');
    display_message(SMALL_NAMES[0], "10秒ほどお待ちください");
    display_message('story_info', get_story_info());

    STAGE = 0;
    NEED_STORY = true;
    NEXT = true;
    RALLY_NUM = -2;
    await PAUSE(0.5);
    await show_next();
}

async function go_top() {
    await stop();
    document.getElementById("top").style.display = "block";
    document.getElementById("about").style.display = "block";
    document.getElementById("story").style.display = "none";
    document.getElementById("form").style.display = "none";
    location.href = '#top';
}

async function go_form() {
    await stop();
    document.getElementById("form").style.display = "block";
    document.getElementById("story").style.display = "none";
    document.getElementById("top").style.display = "none";
    document.getElementById("about").style.display = "none";
    location.href = '#form';
}

async function go_about() {
    await stop();
    document.getElementById("form").style.display = "none";
    document.getElementById("story").style.display = "none";
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

function get_story_info() {
    var res = '';
    if (GENRE != '') {
        res = 'ジャンル:' + GENRE + '<br>';
    }
    res += 'いただいたもの：' + PRESENT + '<br>カテゴリー：' + CATEGORY + '<br>お題：' + THEME + '<br>おとん：' + FATHER;
    return res;
}

function get_tweet_text() {
    var res = '';
    if (GENRE != '') {
        res = 'ジャンル: ' + GENRE + '\n\n';
    }
    res += 'いま「' + PRESENT + '」をいただきましたけどもね・・・\n\n';
    res += 'うちのおかんがね、好きな「' + CATEGORY + '」があるらしいんやけど、その名前を忘れたらしくてね・・・\n\n';
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
    var target = document.getElementById("story_share_button");
    console.log(target.href);
    target.style.display = "block";
    target.href = shareUrl;
    return;
}

async function say(pearson, text){
    console.log("say_" + NAMES[pearson] + ":" + text);

    display_message(SMALL_NAMES[pearson], text);

    const voices = speechSynthesis.getVoices();
    ja_voices = new Array();
    voices.forEach(voice => {
        if(voice.lang.match('ja')) ja_voices.push(voice);
    })

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = ja_voices[pearson];
    utterance.rate = SPEED;
    utterance.volume = VOL;
    speechSynthesis.speak(utterance);

    var i = 0;
    while (speechSynthesis.speaking) {
        await PAUSE(text.length * 0.01 / SPEED);
        i++;
        if (i>=25) {
            speechSynthesis.cancel();
            break;
        }
    }
}

async function get_present(first_stage){

    await say(0, '整いました');
    if (!NEXT) return;

    await say(0, "どうもーAIミルクボーイです。お願いします。");
    if (!NEXT) return;

    PRESENT = first_stage["present"];
    await say(0, 'あーありがとうございますー。ね、今、' + PRESENT + 'をいただきましたけどもね。');
    if (!NEXT) return;

    display_message('story_info', get_story_info());

    await say(0, 'こんなんなんぼあっても良いですからね、ありがたいですよ。いうとりますけどもね。');

    RALLY_NUM++;

    if (STAGE_MAX == 0) await finish();

    return;
}

async function introduction(first_stage){

    // 導入
    if (first_stage["category"] == '') {
        no_story();
        return;
    }

    await say(1, 'うちのおかんがね、好きな' + first_stage["category"] + 'があるらしいんやけど、その名前をちょっと忘れたらしくてね。');
    if (!NEXT) return;
    CATEGORY = first_stage["category"];
    display_message('story_info', get_story_info());

    if (first_stage["prediction1"] != '') {
        await say(0, '好きな' + first_stage["category"] + '忘れてもうて。どうなってんねんそれ。');
        var predictions = first_stage["prediction1"];
        if (first_stage["prediction2"] != '') {
            predictions += '」か「' + first_stage["prediction2"];
        }
        await say(0, 'ほんでもおかんが好きな' + first_stage["category"] + 'なんて、「' + predictions + '」くらいでしょう。');
        await say(1, 'それが違うらしいねんな');
    }

    await say(0, 'ほんだら俺がね、おかんの好きな' + first_stage["category"] + '一緒に考えてあげるから、どんな特徴言うてたかとか教えてみてよ。');
    RALLY_NUM++;
}

async function no_story() {
    await say(1, 'うちのおかんがね、最近はあんまり物忘れをしないらしくてね');
    await say(0, 'ほな、漫才にならんやないかい！');
    finish();
}

async function print_stage(stage_obj){
    switch (RALLY_NUM) {
        case 0:
            // 正しい特徴
            await say(1, stage_obj["featX"]);
            if (!NEXT) return;
            await say(0, stage_obj["featX_reply"]);
            if (STAGE == 0) {
                THEME = stage_obj["theme"];
                display_message('story_info', get_story_info());
            }
            RALLY_NUM++;
            return;

        case 1:
            // 誤った特徴
            await say(1, stage_obj["anti_featX"])
            if (!NEXT) return;
            await say(0, stage_obj["anti_featX_reply"]);
            if (stage_obj["next_is_last"]) {
                STAGE = -1;
                RALLY_NUM = 0;
                NEED_STORY = true;
            }
            else RALLY_NUM++
            return;

        case 2:
            // 次のターンへの接続
            await say(0, stage_obj["conjunction"]);
            STAGE++;
            RALLY_NUM = 0;
            NEED_STORY = true;
            return;
  }
}

async function drop(last_stage){
    // 締め
    switch (RALLY_NUM) {
        case 0:
            await say(1, last_stage["featX"]);
            if (!NEXT) return;
            await say(0, last_stage["featX_reply"]);
            RALLY_NUM++;
            return;

        case 1:
            await say(1, last_stage["anti_featX"]);
            if (!NEXT) return;
            await say(0, last_stage["anti_featX_reply"]);
            FATHER = last_stage["anti_theme"];
            display_message('story_info', get_story_info());
            RALLY_NUM++;
            return;

        case 2:
            await say(1, last_stage["conjunction"]);
            if (!NEXT) return;
            await say(0, "いや、絶対ちゃうやろ！");
            if (!NEXT) return;
            await say(0, "もうええわ。どうもありがとうございました。");
            STAGE = -3;
            return;
  }
  return;
}

async function finish() {
    STAGE = -3;
    await say(0, "もうええわ。どうもありがとうございました。");
}

async function stop() {
    NEXT = false;
    speechSynthesis.cancel();

    for (var i=0; i<2; i++) {
        var div = document.getElementById(SMALL_NAMES[i]);
        div.innerHTML = "";
    }
}

function skip() {
    speechSynthesis.cancel();
    return;
}

async function show_next() {
    if (STAGE == -3) {
        generate_share_button();
        await say(0, 'このネタが面白かったら下のボタンからシェアをお願いします！');
        if (INF) repeat_start();
        return;
    }

    if (NEED_STORY) {
        getJSON();
        return;
    }

    console.log("=".repeat(50));
    console.log("stage: " + STAGE + " RALLY_NUM: " + RALLY_NUM);

    if (RALLY_NUM == -2) await get_present(CUR_STAGE_OBJ);
    else if (RALLY_NUM == -1) await introduction(CUR_STAGE_OBJ);
    else if (CUR_STAGE_OBJ["stage"] == -1) await drop(CUR_STAGE_OBJ);
    else await print_stage(CUR_STAGE_OBJ);

    if (NEXT) await show_next();
    return;
}

async function getJSON() {
    var req = new XMLHttpRequest();           // XMLHttpRequest オブジェクトを生成する
    req.onload = function () {    // XMLHttpRequest オブジェクトの状態が変化した際に呼び出されるイベントハンドラ
        if (req.readyState == 4 && req.status == 200) { // サーバーからのレスポンスが完了し、かつ、通信が正常に終了した場合
            CUR_STAGE_OBJ = JSON.parse(req.responseText);
            console.log(req.responseText);
            // CUR_STAGE_OBJ = CUR_STAGE_OBJ[0];
            NEED_STORY = false;
            if (NEXT) show_next();
        } else {
            say(0, 'エラーが発生したため、「次のネタ」ボタンを押してやりなおしてください');
        }
    };
    if (GENRE=='') {
        request_url = BASE_URL + "theme?input_theme=" + INPUT_VALUE + "&stage=" + STAGE + "&seed=" + SEED + "&stage_max=" + STAGE_MAX
    } else {
        request_url = BASE_URL + "genre?stage=" + STAGE + "&seed=" + SEED + "&stage_max=" + STAGE_MAX + "&genre=" + GENRE
    }
    console.log(request_url);
    req.open("GET", request_url, true); // HTTPメソッドとアクセスするサーバーの　URL　を指定
    req.send(null);  // 実際にサーバーへリクエストを送信
}