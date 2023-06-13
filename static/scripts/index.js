function toggleGesture(gesture_id) {
    var label = document.querySelector(`label[for=gesture${gesture_id}]`);
    const gesture_name = label.textContent.trim();
    fetch(`/toggle_gesture/${gesture_name}`)
    
    if (label.classList.contains("gesture-on")) {
        label.classList.remove("gesture-on");
        label.classList.add("gesture-off");
    } else {
        label.classList.remove("gesture-off");
        label.classList.add("gesture-on");
    }
}

function toggleRecognition() {
    alert("Not implemented yet!");
}

function hideGui() {
    alert("Not implemented yet!");
}

function adjustGesturesListHeight() {
    var cameraFeedHeight = document.querySelector(".camera-feed").offsetHeight;
    var gesturesList = document.getElementById("gesturesList");
    gesturesList.style.maxHeight = cameraFeedHeight + "px";
}
function adjustCameraFeedSize() {
    var cameraFeed = document.querySelector(".camera-feed");
    var cameraFeedWidth = cameraFeed.offsetWidth;
    var cameraFeedHeight = cameraFeed.offsetHeight;
  
    var videoFrame = document.getElementById("videoFrame");
    videoFrame.src = "/video_feed?width=" + cameraFeedWidth + "&height=" + cameraFeedHeight;
  }

window.addEventListener('DOMContentLoaded', function() {
    adjustGesturesListHeight();
    adjustCameraFeedSize();
});
  
window.addEventListener('resize', function() {
    adjustGesturesListHeight();
    adjustCameraFeedSize();
});

 
function showAddGesturePopup() {
    document.getElementById("addGesturePopupContainer").style.display = "block";
}

function hideAddGesturePopup() {
    document.getElementById("addGesturePopupContainer").style.display = "none";
}

function saveGesture() {
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

function cancelGesture() {
    // Close the popup window without saving
    hideAddGesturePopup();
}

function recordGesture() {
    var gestureNameInput = document.getElementById("gestureName");
    gestureNameInput.classList.remove("error");
    gestureNameInput.value = "";
    gestureNameInput.placeholder = "Gesture Name";

    showAddGesturePopup();
}

function updateFps() {
    fetch('/get_fps')
        .then(response => response.json())
        .then(data => {
            // Update FPS
            const fpsDisplay = document.getElementById('fpsDisplay');
            const gestures = data.gestures;
            fpsDisplay.textContent = `FPS: ${data.fps}`;
        });
}

function updateInfo() {
    fetch('/get_info')
        .then(response => response.json())
        .then(data => {
            const scoresDisplay = document.getElementById('gestureScores');
            const verdictDisplay = document.getElementById('verdictDisplay');
            const verdictContainer = document.getElementById('gestureVerdict');
            const gestures_list = data.gestures;
            const scores_list = data.current_scores;
            const prediciton = data.current_prediction;

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

            scoresDisplay.innerHTML = output;
        });
}

function showEditGesturePopup() {
    document.getElementById("editGesturePopupContainer").style.display = "block";
}

function hideEditGesturePopup() {
    document.getElementById("editGesturePopupContainer").style.display = "none";
}

function cancelEditGesture() {
    // Close the popup window without saving
    hideEditGesturePopup();
}

function saveEditGesture() {
    // Close the popup window without saving
    hideEditGesturePopup();
}

function toggleDetails(event) {
    const toggleButton = event.currentTarget;
    const listItem = toggleButton.closest('.list-group-item');
    const details = listItem.querySelector('.gesture-details');
    const arrowIcon = toggleButton.querySelector('.fas');

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
    }

    const gesture_name = listItem.querySelector('.gesture_label').textContent.trim();
    const dropdown = listItem.querySelector('.action-dropdown');
    fetch('/get_dropdown_options/' + gesture_name)
    .then(response => response.json())
        .then(data => {
            console.log(JSON.stringify(data))
            // Dynamically create and append option elements
            data.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.text = option.text;
                dropdown.appendChild(optionElement);
            });
        });
 }

function updateSliderValue(slider) {
    const sliderValue = slider.nextElementSibling;
    sliderValue.textContent = slider.value;
}

function applyChanges(event) {
    gestureName = event.currentTarget.closest('.list-group-item').querySelector('.gesture_label').textContent.trim();
    const dropdown = event.currentTarget.closest('.list-group-item').querySelector('.action-dropdown');
    const selectedValue = dropdown.options[dropdown.selectedIndex].value;
    const slider = event.currentTarget.closest('.list-group-item').querySelector('.slider');
    const sliderValue = slider.value;

    fetch('/apply_changes/' + gestureName + '/' + selectedValue + '/' + sliderValue)
    toggleDetails(event);
}

function cancelChanges(event) {
    toggleDetails(event);
}


function handleActionChange(event) {
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

function showRecordPopup(listItem) {
    // Display the popup container
    var popupContainer = listItem.querySelector(".record-popup");
    popupContainer.style.display = "block";
}

function startRecording() {
    const recordField = document.getElementById("recordField_"+currentGestureName);
    recordField.onclick = stopRecording;
    recordField.textContent = "Press keys...";
    keys = []
    codes = []
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
}

function updateRecordField() {
    const recordField = document.getElementById("recordField_"+currentGestureName);
    recordField.textContent = keys.map(key => {
        if (key.action === 'down') {
            return key.key + '↓'
        } else {
            return key.key + '↑'
        }
    }).join(' + ');
}

function stopRecording() {
    document.removeEventListener('keydown', handleKeyDown);
    document.removeEventListener('keyup', handleKeyUp);
    const recordField = document.getElementById("recordField_"+currentGestureName);
    recordField.onclick = startRecording;
    recordField.textContent = "Recorded: " + recordField.textContent;
}

function saveCustomKeyCombination() {
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

function cancelRecordPopup() {
    // Hide the popup
    hideRecordPopup();
}

function hideRecordPopup() {
    stopRecording();
    const recordField = document.getElementById("recordField_"+currentGestureName);
    recordField.textContent = "CLICK TO START RECORDING";
    var popupContainer = document.getElementById("recordPopupContainer_"+currentGestureName);
    popupContainer.style.display = "none";
    currentGestureName = "";
}

function handleKeyDown(event) {
    if (event.repeat) { return }
    const key = event.key;
    const code = event.code;
    keys.push({key:key, action:'down'});
    codes.push({key:code, action:'down'});
    updateRecordField();
}

function handleKeyUp(event) {
    if (event.repeat) { return }
    const key = event.key;
    const code = event.code;
    keys.push({key:key, action:'up'});
    codes.push({key:code, action:'up'});
    updateRecordField();
}
  

// Call the updateInfo function every 0.1 seconds
const fpsInterval = setInterval(updateFps, 100);
const dataInterval = setInterval(updateInfo, 100);
var currentGestureName = "";
var keys = [];
var codes = [];