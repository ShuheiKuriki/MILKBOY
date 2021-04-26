const BASE_URL = location.protocol + "//" + location.host + "/milkboy/stage"
const name = ["UTSUMI", "KOMABA"];
const name2 = ["utsumi", "komaba"];
var stage = 0;
var stage_end = true;
var rally_num = -2;
const delay_time = 1;
var cur_stage_obj = null;
var next = true;
const pause = sec => new Promise(resolve => setTimeout(resolve, sec * 1000))

var inputValue = "ミルクボーイ";
var seed = 0;
var inf = false;

async function showMessage(){
  const textbox = document.getElementById("message");
  const num = document.getElementById("seed");
  const num2 = document.getElementById("stage");
  const infinity = document.getElementById("infinity");
  inputValue = textbox.value;
  seed = num.value;
  if (seed<0) seed = Math.floor( Math.random() * 100000 );
  stage_max = num2.value;
  stage = 0;
  stage_end = true;
  rally_num = -2;
  if (infinity.checked) inf = true;
  await stop();
  await say(0, 'ネタを生成中です。');

  show_next();
}

async function say(pearson, text){
  console.log("say_" + name[pearson] + ":" + text);

  var div = document.getElementById(name2[pearson]);
  div.innerHTML = text;

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

async function print_stage(stage, i){
  console.log("rally_num: " + rally_num);

  switch (i) {
    case 0:
      // 正しい特徴
      await say(1, stage["featX"]);
      await say(0, stage["featX_reply"]);
      if (next) show_next();
      break;

    case 1:
      // 誤った特徴
      await say(1, stage["anti_featX"])
      await say(0, stage["anti_featX_reply"]);
      if (next) show_next();

      // 次がもうラストstageの場合，conjunctionはいらない
      if(stage["next_is_last"]){
        return true;
      }

      break;

    case 2:
      // 次のターンへの接続
      await say(0, stage["conjunction"]);
      if (next) show_next();

    default:
      return true;
  }

  return false;
}

async function tsukami(first_stage){
  await say(0, 'できました');
  await say(0, "どうもーミルクボーイです。お願いします。");
  await say(0, 'あーありがとうございますー。ね、今、' + first_stage["tsukami"] + 'をいただきましたけどもね。');
  await say(0, 'こんなんなんぼあっても良いですからね、ありがたいですよ。いうとりますけどもね。');
  if (next) show_next();
}

async function introduction(first_stage){
  // 導入
  await say(1, 'うちのおかんがね、好きな' + first_stage["category"] + 'があるらしいんやけど、その名前をちょっと忘れたらしくてね。');
  await say(0, 'ほんだら俺がね、おかんの好きな' + first_stage["category"] + '一緒に考えてあげるから、どんな特徴言うてたかとか教えてみてよ。');
  if (next) show_next();
}

async function drop(last_stage, i){
  switch (i) {
    case 0:
      // 締め
      await say(1, last_stage["featX"]);
      await say(0, last_stage["featX_reply"]);
      if (next) show_next();
      break;

    case 1:
      await say(1, last_stage["anti_featX"]);
      await say(0, last_stage["anti_featX_reply"]);
      if (next) show_next();
      break;

    case 2:
      await say(1, last_stage["conjunction"]);
      await say(0, "いや、絶対ちゃうやろ！");
      await say(0, "もうええわ。どうもありがとうございました。");
      if (inf) showMessage();

    default:
      return true;
  }

  return false;
}

async function finish() {
  await say(0, "もうええわ。どうもありがとうございました。");
  if (inf) showMessage();
}

async function stop() {
  next = false;
  for (var i=0; i<10; i++) {
    speechSynthesis.cancel();
    await pause(0.2);
  }
  for (var i=0; i<2; i++) {
    var div = document.getElementById(name2[i]);
    div.innerHTML = "";
  }
  next = true;
}

function show_next() {
  var debug = document.getElementById("debug");
  if(stage == -3){
    say(0, '次のネタを押してください');
    return;
  }

  if(stage_end){
    getJSON();
    return;
  }

  console.log("=".repeat(50));
  console.log("stage: " + stage);

  switch (cur_stage_obj["stage"]) {
    case -1:
      if (rally_num == -2) {
        console.log("rally_num:"+rally_num);
        tsukami(cur_stage_obj);
        rally_num = -1;
        break;
      }
      if (rally_num == -1) {
        if (stage_max == 0) finish();
        else {
          introduction(cur_stage_obj);
          rally_num++;
        }
        break;
      }
      rally_end = drop(cur_stage_obj, rally_num);
      if(rally_end){
        rally_num = -1;
        stage = -3;
      }else{
        rally_num++;
      }
      break;

    case -2:
      debug.innerHTML += '<H1>エラーメッセージ</H1>';
      break;

    case 0:
      if(rally_num == -2){
        tsukami(cur_stage_obj);
        rally_num = -1;
        break;
      }
      if(rally_num == -1){
        introduction(cur_stage_obj);
        rally_num = 0;
        break;
      }

    default:
      rally_end = print_stage(cur_stage_obj, rally_num);

      if(rally_end){
        rally_num = 0;
        stage_end = true;
        stage++;

        if(cur_stage_obj["next_is_last"]){
          stage = -1;
        }

      }else{
        rally_num++;
      }
  }
}

function getJSON() {
  var req = new XMLHttpRequest();           // XMLHttpRequest オブジェクトを生成する
  req.onreadystatechange = function () {    // XMLHttpRequest オブジェクトの状態が変化した際に呼び出されるイベントハンドラ
    if (req.readyState == 4 && req.status == 200) { // サーバーからのレスポンスが完了し、かつ、通信が正常に終了した場合
      cur_stage_obj = JSON.parse(req.responseText);
      console.log(req.responseText);
      // cur_stage_obj = cur_stage_obj[0];
      stage_end = false;
      if (next) show_next();
    }
  };

  console.log(BASE_URL + "?input_theme="+ inputValue +"&stage=" + stage + "&seed=" + seed + "&stage_max=" + stage_max)

  req.open("GET", BASE_URL + "?input_theme=" + inputValue + "&stage=" + stage + "&seed=" + seed+ "&stage_max=" + stage_max, false); // HTTPメソッドとアクセスするサーバーの　URL　を指定
  req.send(null);  // 実際にサーバーへリクエストを送信
}