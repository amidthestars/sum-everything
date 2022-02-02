// Template article field and textbox
let current_id = String(+ new Date())
const text_template = document.createElement("p");
const input_template = document.createElement("textarea");
const delay = ms => new Promise(res => setTimeout(res, ms));

input_template.rows = 10;
input_template.placeholder = "Type or paste something...";
text_template.classList.add('mb-8');
input_template.classList.add('inherit', 'p-2', 'w-full', 'rounded-lg', 'border', 'border-gray-400', 'shake-constant');

// Template a history entry
const history_template = document.createElement("li");
const link_template = document.createElement("a");

link_template.classList.add("nav")

// Template an available model
const available_model_template = document.createElement("option");


// Get DOM elements needed to detect text editing and summary
const article_button_container = document.querySelector('.article-button-container');
const summary_button_container = document.querySelector('.summary-button-container');
const copy_summary_buttton = document.querySelector('.js-copy-summary');
const get_summary_button = document.querySelector('.js-get-summary');
const edit_text_toggle = document.querySelector('.js-edit-text');
const remove_text_button = document.querySelector('.js-remove-text');
const new_text_button = document.querySelector('.js-new-text');
const article_area = document.getElementById("article");
const summary_text = document.getElementById("summary-text");

// Get DOM elements related to theme toggling
const dark_mode_toggle = document.querySelector('.js-change-theme');
const body = document.querySelector('body');

// Get DOM elements needed to read text files
const upload_file_buttton = document.querySelector('.js-copy-file');
const file_input = document.getElementById('file-input')

// Get DOM elements related to showing history
const history_button_container = document.querySelector('.history-button-container');
const history_more = document.querySelector('.js-more-history');

// Get model select DOM elements
const available_models = document.querySelector('.available-models');

// Get Alert DOM elements
const article_alert = document.getElementById("article-alert");

// Regex vars
let multinewline = /\n+/g;
let numcol = /grid-cols-\d/g;
