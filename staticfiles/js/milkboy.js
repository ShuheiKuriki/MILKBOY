const BASE_URL = "https://" + location.host + "/milkboy/stage"
var stage = 0;
var stage_end = true;
var rally_num = -2;
const delay_time = 1;
var cur_stage_obj = null;
const pause = sec => new Promise(resolve => setTimeout(resolve, sec * 1000))

var inputValue = "ミルクボーイ";
var seed = 0;
var inf = false;

const showMessage = () => {
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
  please_wait();
  show_next();
}

async function say_UTSUMI(text){
  console.log("say_UTSUMI: " + text);

  var utsumi = document.getElementById("utsumi0");
  text_bom = text;
  utsumi.innerHTML = text_bom;

  const voices = speechSynthesis.getVoices();
  ja_voices = new Array();
  voices.forEach(voice => {
    if(voice.lang.match('ja')) ja_voices.push(voice);
  })
  // console.log(ja_voices)

  const uttr = new SpeechSynthesisUtterance(text);
  uttr.voice = ja_voices[0];
  speechSynthesis.speak(uttr);

  await pause(text.length * 0.15);
  var i = 0;
  while (speechSynthesis.speaking) {
    await pause(text.length * 0.01);
    i++;
    if (i>=10) {
      speechSynthesis.cancel();
      break;
    }
  }
}

async function say_KOMABA(text){
  console.log("say_KOMABA: " + text);

  var komaba = document.getElementById("komaba0");
  text_bom = text;
  komaba.innerHTML = text_bom;

  const voices = speechSynthesis.getVoices();
  ja_voices = new Array();
  voices.forEach(voice => {
    if(voice.lang.match('ja')) ja_voices.push(voice);
  })
  // console.log(ja_voices);

  const uttr = new SpeechSynthesisUtterance(text);
  uttr.voice = ja_voices[Math.min(1,ja_voices.length-1)];
  speechSynthesis.speak(uttr);

  await pause(text.length * 0.15);
  var i = 0;
  while (speechSynthesis.speaking) {
    await pause(text.length * 0.01);
    i++;
    if (i>=8) {
      speechSynthesis.cancel();
      break;
    }
  }
}

function please_wait() {
    (async() => {
        await say_UTSUMI('ネタを生成中です。');
    }) ()
}

function print_stage(stage, i){
  console.log("rally_num: " + rally_num);

  switch (i) {
    case 0:
      (async() => {
        // 正しい特徴
        await say_KOMABA(stage["featX"]);
        await say_UTSUMI(stage["featX_reply"]);
        show_next();
      })()
      break;

    case 1:
      (async() => {
        // 誤った特徴
        await say_KOMABA(stage["anti_featX"])
        await say_UTSUMI(stage["anti_featX_reply"]);
        show_next();
      })()

      // 次がもうラストstageの場合，conjunctionはいらない
      if(stage["next_is_last"]){
        return true;
      }

      break;

    case 2:
      (async() => {
        // 次のターンへの接続
        await say_UTSUMI(stage["conjunction"]);
        show_next();
      })()

    default:
      return true;
  }

  return false;
}

function tsukami(first_stage){
  (async() => {
    // 挨拶
    await say_UTSUMI('できました');
    await say_UTSUMI("どうもーミルクボーイです。お願いします。")
    // つかみ
    await say_UTSUMI('あーありがとうございますー。ね、今、' + first_stage["tsukami"] + 'をいただきましたけどもね。')
    await say_UTSUMI('こんなんなんぼあっても良いですからね、ありがたいですよ。いうとりますけどもね。')
    show_next();
  })()
}

function introduction(first_stage){
  (async() => {
    // 導入
    await say_KOMABA('うちのおかんがね、好きな' + first_stage["category"] + 'があるらしいんやけど、その名前をちょっと忘れたらしくてね。');
    await say_UTSUMI('ほんだら俺がね、おかんの好きな' + first_stage["category"] + '一緒に考えてあげるから、どんな特徴言うてたかとか教えてみてよ。');
    show_next();
  })()
}

function drop(last_stage, i){
  switch (i) {
    case 0:
      (async() => {
        // 締め
        await say_KOMABA(last_stage["featX"]);
        await say_UTSUMI(last_stage["featX_reply"]);
        show_next();
      })()
      break;

    case 1:
      (async() => {
        await say_KOMABA(last_stage["anti_featX"]);
        await say_UTSUMI(last_stage["anti_featX_reply"]);
        show_next();
      })()
      break;

    case 2:
      (async() => {
        await say_KOMABA(last_stage["conjunction"]);
        await say_UTSUMI("いや、絶対ちゃうやろ！");
        await say_UTSUMI("もうええわ。どうもありがとうございました。");
        if (inf) {
          showMessage();
        }
      })()

    default:
      return true;
  }

  return false;
}

function finish() {
  (async() => {
    await say_UTSUMI("もうええわ。どうもありがとうございました。");
    if (inf) showMessage();
  })()
}

function show_next() {
  var debug = document.getElementById("debug");
  if(stage == -3){
    say_UTSUMI('次のネタを押してください');
    return;
  }

  if(stage_end){
    getJSON();
    return;
  }

  console.log("=".repeat(50));
  console.log("stage: " + stage);
  // JSONのキーと値を全部表示する
  // Object.keys(cur_stage_obj).forEach(function(key){
  //   console.log(key + ":" + cur_stage_obj[key]);
  // });
  // console.log("=".repeat(50));

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
      show_next();
    }
  };

  console.log(BASE_URL + "?input_theme="+ inputValue +"&stage=" + stage + "&seed=" + seed + "&stage_max=" + stage_max)

  req.open("GET", BASE_URL + "?input_theme=" + inputValue + "&stage=" + stage + "&seed=" + seed+ "&stage_max=" + stage_max, false); // HTTPメソッドとアクセスするサーバーの　URL　を指定
  req.send(null);  // 実際にサーバーへリクエストを送信
}