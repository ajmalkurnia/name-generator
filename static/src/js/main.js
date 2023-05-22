(function() {
  "use strict";
  
  var httpRequest;
  var generatedName = document.querySelector("#historyName");
  const nameField = document.querySelector("#name");
  const loader = document.getElementById("generateButton").nextElementSibling
  nameField.textContent = "_".repeat(16);
  document.getElementById("generateButton").onclick = function() {
    var seed = document.getElementById("seed").value;
    var maxChar = document.getElementById("maxCharacter").value;
    var maxWord = document.getElementById("maxWord").value;

    if (nameField.textContent[0] != "_" && !nameField.textContent.startsWith("E:")) {
      const li = document.createElement("li");
      const p = document.createElement("p");
      const button = document.createElement("button");
      p.textContent = nameField.textContent;
      button.className = "copy-button";
      button.innerHTML = "<span class='ic-copy'></span><span class='copy-tooltip'>Copied !</span>";
      button.onclick = copySiblingText
      li.appendChild(p);
      li.appendChild(button);
      generatedName.prepend(li);
    }
    this.disabled = true;
    makeRequest(seed, maxChar, maxWord);
  };

  function showTooltip(elem) {
    elem.style.opacity = "1";
    elem.style.visibility = "visible";
  }

  function hideTooltip(elem) {
    elem.style.opacity = "0";
    elem.style.visibility = "hidden";
  }

  
  function copySiblingText() {
    navigator.clipboard.writeText(this.previousElementSibling.textContent);
    setTimeout(hideTooltip, 500, this.childNodes[1]);
    setTimeout(showTooltip, 100, this.childNodes[1]);
  }

  function wordflick(word1, word2, tick_speed) {
    let offset = word1.length;
    let part
    // var offset2 = word2.length;
    let forwards = false;
    let flicker = setInterval(function () {
      // Remove this element text 
      if (forwards) {
        part = word2.substr(0, offset);
        offset++;
      } else {
        part = word1.substr(0, offset);
        offset--;
      }
      if (offset == 1) {
        forwards = true;
      } else if (offset == word2.length+1 && forwards) {
        window.clearInterval(flicker);
        document.getElementById("generateButton").disabled = false;
      }
      nameField.textContent = part;
    }, tick_speed);
  }

  function makeRequest(seed, maxChar, maxWord) {
    httpRequest = new XMLHttpRequest();
    if (!httpRequest) {
      return false;
    }
    httpRequest.onload = alertContents;
    httpRequest.onload = alertContents;
    httpRequest.open('POST', '/generate');
    httpRequest.setRequestHeader("Content-Type", "application/JSON");
    httpRequest.send(JSON.stringify({
      "seed": seed,
      "max_length": parseInt(maxChar),
      "max_words": parseInt(maxWord)
    }));
    loader.style.visibility = "visible";
  }
  
  function alertContents() {
    loader.style.visibility = "hidden";
    if (httpRequest.status === 200) {
      var response = JSON.parse(httpRequest.responseText);
      wordflick(nameField.textContent, response["name"], 10);
      if (nameField.style["letter-spacing"] != "normal") {
        nameField.style["letter-spacing"] = "normal";
      }
      if (nameField.parentElement.style.backgroundColor != "#161A1D") {
        nameField.parentElement.style["background-color"] = "#161A1D";
      }
    } else {
      // Failed... Somehow
      let msg_text; 
      if (httpRequest.status == 0) {
        msg_text = "E: Unable to Connect";
      } else {
        msg_text = "E: "+httpRequest.statusText;
      }
      if (nameField.textContent != msg_text) {
        wordflick(nameField.textContent, msg_text, 10);
      }
      nameField.parentElement.style["background-color"] = "#300312";
    }
  }

  var button= document.getElementsByClassName('copy-button')[0];
  button.onclick = copySiblingText

  const moreOption = document.getElementById('moreOption');
  moreOption.style.height = "0px";
  document.getElementById('optionButton').onclick = function(){
    if (moreOption.style.height == "0px"){
      moreOption.style.height = moreOption.scrollHeight+"px";
      document.getElementById('optionButton').textContent = "- More Option";
    } else {
      moreOption.style.height = "0px";
      document.getElementById('optionButton').textContent = "+ More Option";
    }
  }

  const charSlider = document.getElementById('maxCharacter');
  charSlider.oninput = function() {
    if (nameField.textContent[0] == "_") {
      nameField.textContent = "_".repeat(charSlider.value);
    }
    char.value = this.value;
  }

  const rangeInputs = document.querySelectorAll('input[type="range"]')

  function setSliderColor(elem) {
    const min = elem.min;
    const max = elem.max;
    const val = elem.value;
    
    elem.style.backgroundSize = (val - min) * 100 / (max - min) + '% 100%';
  }
  function handleInputChange(e) {
    let target = e.target
    if (e.target.type !== 'range') {
      target = document.getElementById('range')
    } 
    setSliderColor(target);
  }

  rangeInputs.forEach(input => {
    setSliderColor(input);
    // input.addEventListener('input', handleInputChange)
    input.addEventListener('input', handleInputChange);
  })

})()
