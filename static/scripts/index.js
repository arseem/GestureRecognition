async function toggleGesture(button, gesture_id) {
    var label = document.querySelector(`label[for=gesture${gesture_id}]`);
    const gesture_name = label.textContent.trim();
    fetch(`/toggle_gesture/${gesture_name}`).then(response => {
        response.json()
        .then(response => {
            if (response.success) {
                if (label.classList.contains("gesture-on")) {
                    label.classList.remove("gesture-on");
                    label.classList.add("gesture-off");
                } else {
                    label.classList.remove("gesture-off");
                    label.classList.add("gesture-on");
                }
            }
            else {
                button.checked = false;
                gestureLabel = button.parentElement.querySelector(".gesture_label");
                // gestureLabel.style.color = "red";
                gestureSpan = gestureLabel.parentElement.querySelector("span");
                if (!gestureSpan.textContent) {
                    gestureSpan.textContent = " (NOT LEARNED)";
                    gestureSpan.style.color = "red";
                }
            }
        });
    });
}

async function toggleRecognition(button) {
    if (button.textContent == "Toggle Recognition OFF") {
        button.textContent = "Toggle Recognition ON";
        button.classList.remove("btn-danger");
        button.classList.add("btn-success");
    }
    else {
        button.textContent = "Toggle Recognition OFF";
        button.classList.add("btn-danger");
        button.classList.remove("btn-success");
    }

    fetch('/toggle_recognition')
}

async function hideGui(button) {
    if (button.textContent == "Enable Overlay") {
        document.getElementById("gui-slider-container").style.opacity = "1";
        button.textContent = "Disable Overlay";
    } else {
        document.getElementById("gui-slider-container").style.opacity = "0";
        button.textContent = "Enable Overlay";
    }

    fetch('/toggle_overlay')
}

async function updateOverlaySize(slider) {
    fetch('/update_overlay_size/' +  slider.value);
}

async function updateOverlayOpacity(slider) {
    fetch('/update_overlay_opacity/' + slider.value);
}

async function adjustGesturesListHeight() {
    var cameraFeedHeight = document.querySelector(".camera-feed").offsetHeight;
    var gesturesList = document.getElementById("gesturesList");
    gesturesList.style.maxHeight = cameraFeedHeight + "px";
}
async function adjustCameraFeedSize() {
    var cameraFeed = document.querySelector(".camera-feed");
    var cameraFeedWidth = cameraFeed.offsetWidth;
    var cameraFeedHeight = cameraFeed.offsetHeight;
  
    var videoFrame = document.getElementById("videoFrame");
    videoFrame.src = "/video_feed?width=" + cameraFeedWidth + "&height=" + cameraFeedHeight;
  }

window.addEventListener('DOMContentLoaded', async function() {
    adjustGesturesListHeight();
    adjustCameraFeedSize();
});
  
window.addEventListener('resize', async function() {
    adjustGesturesListHeight();
    adjustCameraFeedSize();
});

 
async function showAddGesturePopup() {
    document.getElementById("addGesturePopupContainer").style.display = "block";
}

async function hideAddGesturePopup() {
    document.getElementById("addGesturePopupContainer").style.display = "none";
}

async function saveGesture() {
    var gestureNameInput = document.getElementById("gestureName");
    var gestureName = gestureNameInput.value.trim();
    var gestureType = document.querySelector('input[name="gestureType"]:checked').value;
    var gesturesList = document.getElementById("gesturesList");

    if (gestureName === "") {
        gestureNameInput.classList.add("error");
        gestureNameInput.placeholder = "Please enter a valid gesture name";
        return;
    }

    for (var i = 0; i < gesturesList.children.length; i++) {
        var listItem = gesturesList.children[i];
        var listItemText = listItem.querySelector(".custom-control-label").textContent.trim();
        if (listItemText === gestureName) {
            gestureNameInput.classList.add("error");
            gestureNameInput.value = "";
            gestureNameInput.placeholder = "Gesture name already exists";
            return;
        }
    }

    // Perform any necessary actions with the captured gesture name and type
    window.location.href = "/record_gesture/" + gestureName + '/' + gestureType;
    hideAddGesturePopup();
}

async function cancelGesture() {
    // Close the popup window without saving
    hideAddGesturePopup();
}

async function recordGesture() {
    var gestureNameInput = document.getElementById("gestureName");
    gestureNameInput.classList.remove("error");
    gestureNameInput.value = "";
    gestureNameInput.placeholder = "Gesture Name";

    showAddGesturePopup();
}

async function updateFps() {
    fetch('/get_fps')
        .then(response => response.json())
        .then(data => {
            // Update FPS
            const fpsDisplay = document.getElementById('fpsDisplay');
            const gestures = data.gestures;
            fpsDisplay.textContent = `FPS: ${data.fps}`;
        });
}

async function updateInfo() {
    fetch('/get_info')
        .then(response => response.json())
        .then(data => {
            const scoresDisplay = document.getElementById('gestureScores');
            const verdictDisplay = document.getElementById('verdictDisplay');
            const verdictContainer = document.getElementById('gestureVerdict');
            const gestures_list = data.gestures;
            const scores_list = data.current_scores;
            const prediciton = data.current_prediction;
            const needs_training = data.needs_training;

            output = "";
            for (var i = 0; i < gestures_list.length; i++) {
                output += `<div>${gestures_list[i]}: ${scores_list[i]}</div>`;
            }

            if (prediciton) {
                verdictContainer.style.backgroundColor = 'rgba(0, 255, 0, 0.4)';
                verdictDisplay.textContent = `Detected: ${prediciton}`;
            } else {
                verdictContainer.style.backgroundColor = 'rgba(255, 255, 255, 0.4)';
                verdictDisplay.textContent = 'No gesture detected';
            }

            trainingButton = document.getElementById('trainingButton');
            if (trainingButton.textContent != "Training in progress...") {
                if (needs_training ) {
                    trainingButton.style.display = 'block';
                    trainingButton.disabled = false
                    
                } else {
                    trainingButton.style.display = 'none';
                    trainingButton.disabled = true
                }
            }

            scoresDisplay.innerHTML = output;
        });
}

async function toggleDetails(event) {
    const toggleButton = event.currentTarget;
    const listItem = toggleButton.closest('.list-group-item');
    const details = listItem.querySelector('.gesture-details');
    const arrowIcon = toggleButton.querySelector('.fas');
    var checkmarks = details.querySelectorAll('.details-radio');

    if (listItem.classList.contains('expanded')) {
      // Details are currently shown, collapse them
      details.style.maxHeight = '0';
      listItem.classList.remove('expanded');
      arrowIcon.classList.remove('fa-chevron-up');
      arrowIcon.classList.add('fa-chevron-down');
    } else {
      // Details are currently hidden, expand them
      details.style.maxHeight = details.scrollHeight*2 + 'px';
      listItem.classList.add('expanded');
      arrowIcon.classList.remove('fa-chevron-down');
      arrowIcon.classList.add('fa-chevron-up');

      const gesture_name = listItem.querySelector('.gesture_label').textContent.trim();
      const dropdown = listItem.querySelector('.action-dropdown');
      fetch('/get_dropdown_options/' + gesture_name)
      .then(response => response.json())
          .then(data => {
              // Dynamically create and append option elements
              for (var i = dropdown.options.length - 1; i >= 0; i--) {
                  dropdown.remove(i);
              }
              const dropdown_data = data[1];
              const type = data[0];

              const detection_threshold = data[2];
              const slider = listItem.querySelector('.slider-det');
              const sliderValue = slider.nextElementSibling;
              slider.value = detection_threshold;
              sliderValue.textContent = detection_threshold;

              const trakcing_threshold = data[3];
              const slider2 = listItem.querySelector('.slider-track');
              const sliderValue2 = slider2.nextElementSibling;
              slider2.value = trakcing_threshold;
              sliderValue2.textContent = trakcing_threshold;

              dropdown_data.forEach(option => {
                  const optionElement = document.createElement('option');
                  optionElement.value = option.value;
                  optionElement.text = option.text;
                  dropdown.appendChild(optionElement);
              });  
              if (!type) {
                  checkmarks[1].checked = true;
              } else {
                  checkmarks[0].checked = true;
              }  
          });
    }
 }

async function updateSliderValue(slider) {
    const sliderValue = slider.nextElementSibling;
    sliderValue.textContent = slider.value;
}

async function applyChanges(event) {
    gestureName = event.currentTarget.closest('.list-group-item').querySelector('.gesture_label').textContent.trim();
    const dropdown = event.currentTarget.closest('.list-group-item').querySelector('.action-dropdown');
    const selectedValue = dropdown.options[dropdown.selectedIndex].value;
    const sliderDet = event.currentTarget.closest('.list-group-item').querySelector('.slider-det');
    const sliderDetValue = sliderDet.value;
    const sliderTrack = event.currentTarget.closest('.list-group-item').querySelector('.slider-track');
    const sliderTrackValue = sliderTrack.value;
    const checkmarks = event.currentTarget.closest('.list-group-item').querySelector('.gesture-details').querySelectorAll('.details-radio');

    if (checkmarks[0].checked) {
        mode = "1";
    } else {
        mode = "0";
    }

    fetch('/apply_changes/' + gestureName + '/' + selectedValue + '/' + sliderDetValue + '/' + sliderTrackValue + '/' + mode)
    toggleDetails(event);
}

async function cancelChanges(event) {
    toggleDetails(event);
}


async function handleActionChange(event) {
    var selectedValue = event.currentTarget.value;
    console.log(selectedValue)
    const listItem = event.currentTarget.closest('.list-group-item');
    currentGestureName = listItem.querySelector('.gesture_label').textContent.trim();

    if (selectedValue === "RECORDNEW") {
      // Show the popup
      showRecordPopup(listItem);
    } else {
      // Perform other actions for different values
      // Add your logic here
    }
}

async function showRecordPopup(listItem) {
    // Display the popup container
    var popupContainer = listItem.querySelector(".record-popup");
    popupContainer.style.display = "block";
}

async function startRecording() {
    const recordField = document.getElementById("recordField_"+currentGestureName);
    recordField.onclick = stopRecording;
    recordField.textContent = "Press keys...";
    keys = []
    codes = []
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
}

async function updateRecordField() {
    const recordField = document.getElementById("recordField_"+currentGestureName);
    recordField.textContent = keys.map(key => {
        if (key.action === 'down') {
            return key.key + '↓'
        } else {
            return key.key + '↑'
        }
    }).join(' + ');
}

async function stopRecording() {
    document.removeEventListener('keydown', handleKeyDown);
    document.removeEventListener('keyup', handleKeyUp);
    const recordField = document.getElementById("recordField_"+currentGestureName);
    recordField.onclick = startRecording;
    recordField.textContent = "Recorded: " + recordField.textContent;
}

async function saveCustomKeyCombination() {
    const listItem = document.getElementById("listItem_"+currentGestureName)
    const dropdown = listItem.querySelector('.action-dropdown');

    var gestureName = listItem.querySelector('.gesture_label').textContent.trim();
    console.log(gestureName);

    const newOption = document.createElement('option');
    newOption.value = JSON.stringify(codes);
    newOption.text = 'CUSTOM';

    for (var i = 0; i < dropdown.options.length; i++) {
        if (dropdown.options[i].text === newOption.text) {
            dropdown.remove(i);
            break;
        }
    }

    dropdown.appendChild(newOption);

    for (var i = 0; i < dropdown.options.length; i++) {
        if (dropdown.options[i].text === newOption.text) {
            dropdown.selectedIndex = i;
            break;
        }
    }
  
    // Hide the popup
    hideRecordPopup();
}

async function cancelRecordPopup() {
    // Hide the popup
    hideRecordPopup();
}

async function hideRecordPopup() {
    stopRecording();
    const recordField = document.getElementById("recordField_"+currentGestureName);
    recordField.textContent = "CLICK TO START RECORDING";
    var popupContainer = document.getElementById("recordPopupContainer_"+currentGestureName);
    popupContainer.style.display = "none";
    currentGestureName = "";
}

async function handleKeyDown(event) {
    if (event.repeat) { return }
    const key = event.key;
    const code = event.code;
    keys.push({key:key, action:'down'});
    codes.push({key:code, action:'down'});
    updateRecordField();
}

async function handleKeyUp(event) {
    if (event.repeat) { return }
    const key = event.key;
    const code = event.code;
    keys.push({key:key, action:'up'});
    codes.push({key:code, action:'up'});
    updateRecordField();
}

async function saveState() {
    fetch('/save_state')
}

async function loadState() {
    fetch('/load_state').then(response => location.reload())
}

async function startRecordingGesture() {
    var gestureNameInput = document.getElementById("gestureName");
    var gestureName = gestureNameInput.value;
    console.log(gestureName)
    if (gestureName === "") {
        alert("Please enter a name for the gesture");
        return;
    }

    fetch('/start_recording/' + gestureName).then(response => {
        response.json().then(data => {
            if (data.status === 200) {
                hideAddGesturePopup();
                document.querySelectorAll(".cam-overlay").forEach(x => x.style.display = "none");

                var videoFrame = document.getElementById("videoFrame");
                videoFrame.src = videoFrame.src;

                recordingInterval = setInterval(checkRecordingState, 500);
            } else {
                alert("Gesture with the same name already exists");
            }
        });
    });
}

function checkRecordingState() {
    fetch('/is_recording_done').then(response => {
        response.json().then(data => {
            if (data.status === 200) {
                fetch('/stop_recording').then(response => {
                    clearInterval(recordingInterval);
                    document.querySelectorAll(".cam-overlay").forEach(x => x.style.display = "block");
                    location.reload();
                });
            }
        });
    });
}

async function trainNewModel(button) {
    fetch('/start_training').then(response => {
        response.json().then(data => {
            if (data.success) {
                button.textContent = "Training in progress...";
                button.disabled = true;
                trainingInterval = setInterval(checkTrainingState, 2000);
            }
        });
    });
}

async function checkTrainingState() {
    fetch('/is_training_done').then(response => {
        response.json().then(data => {
            if (data.status === 200) {
                fetch('/finish_training').then(response => {
                    document.getElementById("trainingButton").style.display = 'none';
                    document.getElementById("trainingButton").textContent = 'Model outdated, click to train';
                    location.reload();
                    clearInterval(trainingInterval);
                });
            }
        });
    });
}

// Call the updateInfo async function every 0.1 seconds
const fpsInterval = setInterval(updateFps, 100);
const dataInterval = setInterval(updateInfo, 100);
var recordingInterval = null;
var trainingInterval = null;
var currentGestureName = "";
var keys = [];
var codes = [];