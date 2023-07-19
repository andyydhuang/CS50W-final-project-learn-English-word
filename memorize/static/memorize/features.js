var FAVOR_VALUE = "I Like";
var UNFAVOR_VALUE = "Cancel Like";

var MyTest = {};
var NAME_FONT_SIZE = "20px";

const titles = new Map([
  ["home", 'Learning English Words'],
  ["search", 'Get The Meaning'],
  ["test", 'Take The Challenge'],
  ["upload", 'Extend Your Words'],
  ["favorite", 'See The Favorites'],
  ["user-favorite", 'See Your Favorite'],
]);

const sections = ['feature', 'search', 'test', 'upload', 'favorite' ];
const display_sections = ['home', 'search', 'test', 'upload', 'favorite', 'user-favorite'];

document.addEventListener('DOMContentLoaded', function() {
  let hook_type = null;
  let option;

  document.addEventListener("click", function(event){
    //console.log(`event.target:${event.target}`);

    let hookTarget = event.target.closest('[hook-type]');
    //console.log(`hookTarget.innerHTML:${hookTarget.innerHTML}`);

    if (hookTarget == null) {
      return;
    }
    hook_type = hookTarget.getAttribute('hook-type');
    console.log(`hook_type:${hook_type}`);

    option = {
      'event': event,
      'hook_type': hook_type,
      'hook_target': hookTarget
    };

    if (display_sections.includes(hook_type)) {
      load_box(option);
    } else if (hook_type === 'favorite-define') {
      load_favorite_word(event, hookTarget);
    } else if (hook_type === 'hide-menu') {
      hideMenu(event);
    } else if (hook_type === 'show-menu') {
      showMenu(event);
    } else if (hook_type.includes('action')) {
      if (hook_type === 'action-search') {
        search_word(event);
      } else if (hook_type === 'action-play') {
        playItHere(event);
      } else if (hook_type === 'action-add-word-info') {
        add_word_info(event);
      } else if (hook_type === 'action-favor') {
        modify_favor(event, hookTarget);
      } else if (hook_type === 'action-tests-select') {
        run_tests(event, hookTarget);
      } else if (hook_type === 'action-verify') {
        verify_answer(event);
      } else if (hook_type === 'action-next-test') {
        word_test(event);
      } else if (hook_type === 'action-favorites-select') {
        display_favorites(event, hookTarget);
      } else if (hook_type === 'action-show-test-mimgs') {
        show_test_images(event);
      } else if (hook_type === 'action-show-test-audios') {
        show_test_audios(event);
      } else if (hook_type === 'action-show-test-ans') {
        show_test_answer(event);
      } else if (hook_type === 'action-upload') {
        show_processing(event);
      }
    }
  });

  let cur_hook_type = document.querySelector('[cur-hook-type]').getAttribute("cur-hook-type");
  //console.log(`cur_hook_type: ${cur_hook_type}`);

  if (cur_hook_type == 'upload'){
    option = {
      'event': null,
      'hook_type': 'upload'
    };
  } else {
    option = {
      'event': null,
      'hook_type': 'home'
    };
  }
  load_box(option);

});

function showMenu(){
  let navLinks = document.querySelector('#navLinks');
  navLinks.style.right = "0";
}
function hideMenu(){
  let navLinks = document.querySelector('#navLinks');
  navLinks.style.right = "-200px";
} 

function load_box(option) {
  console.log(`load_box: ${option.hook_type}`);
  if (option.event != null) { 
    option.event.preventDefault();
  }

  let ele_header = document.querySelector('#header');
  ele_header.style.display = 'block';
  ele_header.querySelector('.text-box > h1').innerText = titles.get(option.hook_type);

  if (option.hook_type == 'home') {
    ele_header.classList.add('header');
    ele_header.classList.remove('sub-header');
  } else {
    ele_header.classList.add('sub-header');
    ele_header.classList.remove('header');
  }
  load_section(option);
}

function load_section(option){
  let shows = [];
  if (option.hook_type == 'home'){
    shows.push('feature');
  } else if (option.hook_type == 'user-favorite'){
      shows.push('favorite');
  } else {
    shows.push(option.hook_type);
  }
  
  if (option.hook_type == 'search'){
    document.querySelector('.search').querySelector('#word-info').style.display = 'none';
    document.querySelector('.search').querySelector('#search-body').value = '';
    document.querySelector('#search-form').style.display = 'flex';
  } else if (option.hook_type == 'test' || option.hook_type == 'favorite'){
    document.querySelector('div[cur-hook-type]').setAttribute('cur-hook-type', option.hook_type);
    document.querySelector('#answer-form').style.display = 'flex';

    let ele = document.querySelector(`.${option.hook_type}`);
    if (option.hook_type == 'test') {
      ele.querySelector('#test-view-1').style.display = 'block';
      ele.querySelector('#test-empty').innerHTML = '';

      ele_test_view_2 = ele.querySelector('#test-view-2');
      ele_test_view_2.style.display = 'none';
      ele_test_view_2.querySelector('#word').innerHTML = '';
      ele_test_view_2.querySelector('#defn').innerHTML = '';
    } else if (option.hook_type == 'favorite') {
      ele = document.querySelector(`.${option.hook_type}`);
      ele.querySelector('#favorite-view-1').style.display = 'block';
      ele.querySelector('#favorite-view-2').style.display = 'none';
      ele.querySelector('#contents').innerHTML = '';
    }
    load_all_usernames(ele);
  } else if (option.hook_type == 'upload'){
    if (option.event != null) { 
      let ele = document.querySelector('#upload-content-view');
      if (ele != null) ele.innerHTML = '';
    }
  } else if (option.hook_type == 'user-favorite'){
    document.querySelector('div[cur-hook-type]').setAttribute('cur-hook-type', option.hook_type);

    let ele = document.querySelector('.favorite');
    ele.querySelector('#favorite-view-1').style.display = 'none';
    ele.querySelector('#favorite-view-2').style.display = 'block';
  
    let ele_favorite_view_2 = document.querySelector('#favorite-view-2');
    let ele_contents = ele_favorite_view_2.querySelector('#contents');
    ele_contents.innerHTML = '';
    let username = option.hook_target.innerText;
    load_user_words(username);
  } 

  for (let i = 0; i < sections.length; i++) {
    if (shows.includes(sections[i]))  
      document.querySelector(`.${sections[i]}`).style.display = 'block';
    else
      document.querySelector(`.${sections[i]}`).style.display = 'none';
  }
}

const load_all_usernames = async (ele_view) => {
  try {
    await fetch(`/users`)
    .then(response => response.json())
    .then(data => {
      //console.log({data})
      let ele_select = ele_view.querySelector('select');
      create_name_elements(data.all_names, ele_select);
    });
  } catch (err) {
      console.log(`%c ${err}`, 'color: red; font-weight: bold;')
  }
}

const load_user_words = async (username) => {
  try {
      const res = await fetch(`/users/${username}`)
      .then(response => response.json())
      .then(data => {
        //console.log({data})

        MyTest.selected_names = [];
        MyTest.test_words = [];

        MyTest.selected_names[0] = username
        MyTest.test_words[0] = data.favor_word_list;
        MyTest.old_word = '';

        fill_words();
      });
  } catch (err) {
    console.log(`%c ${err}`, 'color: red; font-weight: bold;')
  }
}

function show_processing(event) {
  let ele = document.querySelector('#upload-content-view')
  if (ele != null)
    ele.innerHTML = '';

  let file = document.querySelector('input[type=file]').files[0];
  let extension = file.name.substr( file.name.indexOf('.') + 1 );

  if (extension !== 'xlsx') {
    window.alert("Only Support .xlsx File");
    event.preventDefault();
  } else if (file != null) {
    let ele_upload_view = document.querySelector('.upload > .about-word');
    let ele_to_insert = 
    `
    <div id="loader">
    </div>
    `;
    ele_upload_view.insertAdjacentHTML('beforeend', ele_to_insert);
  }
}

function search_word(event) {
  event.preventDefault();

  document.querySelector('div[cur-hook-type]').setAttribute('cur-hook-type', 'search');

  let compose_ele = document.querySelector('#search-form');
  const formData = new FormData(compose_ele); 
  console.log(...formData)

  let object = {}
  formData.forEach(function(value, key) {
    console.log(`[${key}]:[${value}]`)
    object[key] = value;
  });
  //console.log(object["body"])   

  load_word_info(
    document.querySelector('.search').querySelector('#word-info'),
    object["body"],
  );
}

async function load_word_info(ele_word_info_view, word_name) {

  try {
    let ele_to_insert = 
    `
    <div id="loader">
    </div>
    `;
    ele_word_info_view.parentElement.insertAdjacentHTML('afterbegin', ele_to_insert);

    let type = document.querySelector('div[cur-hook-type]').getAttribute('cur-hook-type');

    const response = await fetch(`/define/${word_name}`);
    const data = await response.json();
    console.log({data})
    ele_word_info_view.parentElement.querySelector('#loader').remove();

    const status = response.status;  
    if (status !== 200) {
      throw "search word failed"
    }
    ele_word_info_view.style.display = 'block';

    ele_word_info_view.querySelector('#word').innerHTML = data.name;
    ele_word_info_view.querySelector('#defn').innerHTML = data.defn;
    if (type == 'search')
        document.querySelector('.search').querySelector('#search-body').value = ''; 

    if (data.defn.indexOf(" not found.</b>") == -1) {
      create_audio_elements(data.phrases, ele_word_info_view);
      if (type == 'search' || type == 'user-favorite')
        load_favor_button(data.is_in_favor, ele_word_info_view);
      display_mimages(data.mimgs, ele_word_info_view);
    } else {
      ele_word_info_view.querySelector('#audios').innerHTML = '';
      ele_word_info_view.querySelector('#mimgs').innerHTML = '';
      ele_word_info_view.querySelector("#modify-favor").innerHTML = '';
      ele_word_info_view.querySelector("#modify-favor").className = '';   
    }
  }
  catch (err) {
    console.log(`%c ${err}`, 'color: red; font-weight: bold;')
  }
}

function create_audio_elements(audio_data_list, ele_word_view) {
  let ele_audios_view = ele_word_view.querySelector('#audios');
  ele_audios_view.innerHTML = '';
  //for (const [key, value] of Object.entries(audio_datas)) {
    //console.log(key, value);
  for (let i = 0; i < audio_data_list.length; i++) {
    const key = audio_data_list[i].name;
    const value = audio_data_list[i].audio_link;
    let ele_to_insert = 
      `
      <div class="audio">  
          <a href="${value}" hook-type="action-play">
              <i class="fa fa-play"></i>
              ${key}
          </a>
      </div>
      `;
      ele_audios_view.insertAdjacentHTML('beforeend', ele_to_insert);
  }
}

function display_mimages(mimgs, ele_word_view) {
  let ele_word_mimgs = ele_word_view.querySelector('#mimgs');
  ele_word_mimgs.innerHTML = '';
  for (let i = 0; i < mimgs.length; i++) {
    let ele_div = document.createElement('div');
    ele_div.classList.add('mimg-col');
    console.log(mimgs[i]);
    img = document.createElement('img');
    img.src = mimgs[i];
    ele_div.appendChild(img);
    ele_word_mimgs.appendChild(ele_div);
  }
}

function load_favor_button(is_in_favor, ele_word_info_view) {
  let ele_modify_favor = ele_word_info_view.querySelector("#modify-favor");
  ele_modify_favor.innerHTML = '';
  ele_modify_favor.classList.add('border', 'btn', 'modify-favor');

  if (is_in_favor) {
    favor_action = false;
    let ele_to_insert = 
      `<i class="fa fa-thumbs-up"></i>`;
      ele_modify_favor.insertAdjacentHTML('beforeend', ele_to_insert);
  } else {
    favor_action = true;
    let ele_to_insert = 
      `<i class="fa fa-thumbs-o-up"></i>`;
      ele_modify_favor.insertAdjacentHTML('beforeend', ele_to_insert);
  }
  ele_modify_favor.setAttribute('favor_action', favor_action);
}

function playItHere(e) {
  let ele_link = e.target.closest('a');

  var audio = document.createElement("audio");
  var src = document.createElement("source");
  src.src = ele_link.href;

  audio.appendChild(src);
  audio.play();
  e.preventDefault();
}

function add_word_info(event) {
  document.querySelector('#to-add-work-info').style.display = 'none';
  document.querySelector('#adding-work-info').style.display = 'block';  
}

function modify_favor(event, hookTarget) {
  favor_action = hookTarget.getAttribute('favor_action');
  //console.log(`favor_action:%c ${favor_action}`, 'color: green; font-weight: bold;')
  let username = document.querySelector('a[hook="req-username"]').innerText;

  const set_favor = async (username, favor_action) =>  {
    try {
      let word = hookTarget.closest('div[id="word-info"]').querySelector('#word').innerText;
      //console.log(word)
      
      let object = {
        "favor_action": favor_action,
    		"word": word
      }
      let jsonData = JSON.stringify(object);
      const response = await fetch(`/users/${username}`, {
        method: 'PUT',
        body: jsonData
      });

      const status = response.status;
      if (status !== 204) {
        throw "modify favor failed"
      }
      await fetch(`/users/${username}/${word}`)
      .then(response => response.json())
      .then(data => {
        console.log({data})
        update_favor_button(data, hookTarget);
      });
    } catch (err) {
      console.log(`%c ${err}`, 'color: red; font-weight: bold;')
    }
  }
  set_favor(username, favor_action);
}

function update_favor_button(data, hookTarget) {   
  let ele_modify_favor = hookTarget.closest('div[id="word-info"]').querySelector('#modify-favor');
  let ele_icon = ele_modify_favor.querySelector('i');
  if (data.is_in_favor) {
    favor_action = false;
    ele_icon.classList.add('fa-thumbs-up'); 
    ele_icon.classList.remove('fa-thumbs-o-up');
  } else {
    favor_action = true;
    ele_icon.classList.add('fa-thumbs-o-up'); 
    ele_icon.classList.remove('fa-thumbs-up');
  }
  ele_modify_favor.setAttribute('favor_action', favor_action);
}

function create_word_element(word , ele_view) {
  let ele_to_insert = 
    `
    <div class="nav-item favorite-words-col" hook-type="favorite-define">
    <a href="#"><strong>${word}</strong></a>
    </div>
    `;
    ele_view.insertAdjacentHTML('beforeend', ele_to_insert);
}

function load_favorite_word(event, hookTarget) {
  event.preventDefault();

  let word_name = hookTarget.innerText
  //console.log(`%c ${word_name}`, 'color: red; font-weight: bold;')
  load_word_info(
    document.querySelector('.favorite').querySelector('#word-info'),
    word_name,
  );
}

function create_name_elements(all_names, ele_select) {
  ele_select.innerHTML = '';
  //for (const [key, value] of Object.entries(audio_datas)) {
  //  console.log(key, value);
  for (let i = 0; i < all_names.length; i++) {
    const username = all_names[i];
    let ele_to_insert = 
      `
      <option value="${username}">${username}</option>
      `;
      ele_select.insertAdjacentHTML('beforeend', ele_to_insert);
  }
}

async function get_select_values_then_load_favorites(hookTarget) {
  let el_select = hookTarget.parentNode.querySelector('select')
  let selected_names = []
  let options = el_select && el_select.options
  let opt;

  for (let i = 0; i < options.length; i++) {
    opt = options[i];
    if (opt.selected) {
      selected_names.push(opt.value || opt.text);
    }
  }
  //console.log(`${selected_names}`)

  let test_words = [] 

  const get_favors = async (selected_names) =>  {
    promises = []
    test_words = []
    try {
      for (let i = 0; i < selected_names.length; i++) {
        promises[i] = await fetch(`/users/${selected_names[i]}`)
        .then(response => response.json())
        .then(data => {
          console.log({data})
          if (data['error'])
            test_words[i] = []; 
          else
            test_words[i] = data.favor_word_list;
        });
      }
      const results = await Promise.allSettled(promises);
      for (let i = 0; i < results.length; i++) {
        if (results[i].status !== 'fulfilled')
          throw "get favors failed"
      }
      MyTest.selected_names = selected_names
      MyTest.test_words = test_words;
      MyTest.old_word = '';
      
      word_test()
    } catch (err) {
      console.log(`%c ${err}`, 'color: red; font-weight: bold;')
    }
  }
  await get_favors(selected_names);
}

async function display_favorites(event, hookTarget) {
  event.preventDefault();

  document.querySelector('#favorite-view-1').style.display = 'none';
  document.querySelector('#favorite-view-2').style.display = 'block';

  await get_select_values_then_load_favorites(hookTarget)

  fill_words();
}

function fill_words (){
  let ele_favorite_view_2 = document.querySelector('#favorite-view-2');
  let ele_contents = ele_favorite_view_2.querySelector('#contents');
  ele_contents.innerHTML = '';

  ele_favorite_view_2.querySelector('#word-info').style.display = 'none';

  for (let i = 0; i < MyTest.selected_names.length; i++) {

    let ele_to_insert = 
    `
    <p style="font-size:${NAME_FONT_SIZE};">${MyTest.selected_names[i]}</p>
    `;
    ele_contents.insertAdjacentHTML('beforeend', ele_to_insert);

    ele_to_insert = 
    `
    <div class="words" id="words-${i}"></div>
    `;
    ele_contents.insertAdjacentHTML('beforeend', ele_to_insert);

    let ele_div_words = ele_favorite_view_2.querySelector(`#words-${i}`);

    if (MyTest.test_words[i].length == 0) {
      ele_to_insert =
      `
      <div id="empty">
      <i class="fa fa-grav fa-lg"></i>
      <span>No Favorite Words</span>
      </div>
      `;
      ele_div_words.insertAdjacentHTML('beforeend', ele_to_insert);
    } else {
      for (let j = 0; j < MyTest.test_words[i].length; j++) {
        create_word_element(MyTest.test_words[i][j], ele_div_words);
      }
    }
  }
}

function run_tests(event, hookTarget) {
  event.preventDefault();
  console.log('get_select_values')
  console.log(hookTarget.innerHTML)
  console.log(hookTarget.parentNode.innerHTML)

  get_select_values_then_load_favorites(hookTarget)
}

function load_test_word(word_name) {
 
  const load_word_content = async (word_name) => {
    try {
      await fetch(`/define/${word_name}`)
      .then(response => response.json())
      .then(data => {
        console.log({data})
        let ele_test = document.querySelector('.test');
        let ele_word_info_view = ele_test.querySelector('#word-info');
        ele_word_info_view.querySelector('#word').innerHTML = data.name;
        ele_word_info_view.querySelector('#word').style.display = 'none'
        ele_word_info_view.querySelector('#defn').innerHTML = data.defn;
   
        ele_word_info_view.querySelector('#audios').style.display = 'none'
        create_audio_elements(data.phrases, ele_word_info_view);
        ele_word_info_view.querySelector('#mimgs').style.display = 'none'
        display_mimages(data.mimgs, ele_word_info_view);
      });
    } catch (err) {
        console.log(`%c ${err}`, 'color: red; font-weight: bold;')
    }
  }
  load_word_content(word_name);
}

function word_test() {
  let ele_test  = document.querySelector('.test');
  ele_test.querySelector('#test-view-1').style.display = 'none';
  ele_test.querySelector('#test-view-2').style.display = 'block';
  ele_test.querySelector('#test-result').style.display = 'none';
  let ele_test_view_2 = ele_test.querySelector('#test-view-2');

  //Merge arrays into one array
  let flat_test_words = MyTest.test_words.flat(1);

  if (ele_test.querySelector('#empty') != null) {
    ele_test.querySelector('#empty').remove();
  }

  if (flat_test_words.length == 0){
    ele_test.querySelector('#test-view-2').style.display = 'none';
    let ele_test_empty = ele_test.querySelector('#test-empty')
    let ele_to_insert =
    `
    <i class="fa fa-grav fa-lg"></i>
    <span>No Favorite Words</span>
    `;
    ele_test_empty.insertAdjacentHTML('afterbegin', ele_to_insert);
  } else {
    let cur_word = '';
      do {
        cur_word = flat_test_words[Math.floor(Math.random() * flat_test_words.length)];
      }
      while (MyTest.old_word === cur_word && flat_test_words.length > 1)
    
      load_test_word(cur_word);
      MyTest.old_word = cur_word;
  }
}

function verify_answer(event) {
  event.preventDefault();

  let answer_ele = document.querySelector('#answer-form');
  const formData = new FormData(answer_ele); 
  console.log(...formData)

  let object = {}
  formData.forEach(function(value, key) {
    console.log(`[${key}]:[${value}]`)
    object[key] = value;
  });
  //console.log(object["body"])

  let ele_tests_view = document.querySelector('.test')
  ele_tests_view.querySelector('#test-result').style.display = 'block';
  let ele_word_info_view = ele_tests_view.querySelector('#word-info');
  let ans = ele_word_info_view.querySelector('#word').innerHTML
  //console.log(`ans:${ans}`)
  let yours = object["body"]
  let correct_letters = 0;
  let ele_test_result = ele_tests_view.querySelector('#test-result');
  ele_test_result.style.display = 'block';
  ele_test_result.querySelector('.fa-pagelines').style.display = 'none';
  ele_test_result.querySelector('.fa-envira').style.display = 'none';
  ele_test_result.querySelector('span').setAttribute("style", "font-weight: bold;");


  let occurence = [];
  if (yours != ans) {
    for (let i = 0; i < yours.length; i++) {
      let index = ans.indexOf(yours[i])
      if (!occurence.includes(index) && index > -1)
      {
        occurence.push(index)
        correct_letters++;
      }
    }
    ele_test_result.querySelector('.fa-envira').style.display = 'block';
    ele_test_result.querySelector('.fa-envira > span').innerHTML = ` ${correct_letters} Letters Conrrect`;
  } else {
    ele_test_result.querySelector('.fa-pagelines').style.display = 'block';
    ele_test_result.querySelector('.fa-pagelines > span').innerHTML = ' Pass';
  }
}

function show_test_images(event) {
  event.preventDefault();
  let ele_tests_view = document.querySelector('.test');
  ele_tests_view.querySelector('#mimgs').style.display = 'flex'
}

function show_test_audios(event) {
  event.preventDefault();

  let ele_tests_view = document.querySelector('.test');
  ele_tests_view.querySelector('#audios').style.display = 'block';

  if (ele_tests_view.querySelector('#audios').querySelector('.audio') == null){
    ele_to_insert =
    `
    <div id="empty">
    <i class="fa fa-grav fa-lg"></i>
    <span>No Audios</span>
    </div>
    `;
    ele_div_words.insertAdjacentHTML('beforeend', ele_to_insert);
  }
}

function show_test_answer(event) {
  event.preventDefault();
  let ele_tests_view = document.querySelector('.test');
  ele_tests_view.querySelector('#word').style.display = 'block'
}