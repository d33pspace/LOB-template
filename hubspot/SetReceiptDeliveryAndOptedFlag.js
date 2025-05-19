// Websites update HubSpot and China website creates Xero invoice, https://zapier.com/editor/227919380/draft/273193436/fields
const existingReceiptPreference = inputData.existingReceiptPreference || 'Email';
const sendCommunicationFlag = inputData.sendCommunicationFlag || 'Y';
const sendReceiptFlag = inputData.sendReceiptFlag || 'Y';
const serverLocation = inputData.serverLocation || 'CN';
const useMockEmail = parseInt(inputData.useMockEmail, 10) || -1; // Fallback to -1 if parsing fails

// Determine optedValue based on communication and receipt flags
let optedValue = 'true';

if (sendReceiptFlag === 'Y' && sendCommunicationFlag === 'Y') {
	optedValue = 'false';
}

// Determine default receipt preference
let finalReceiptPreference;
if (sendReceiptFlag === 'N') {
  finalReceiptPreference = 'Manual';
} else {
  finalReceiptPreference = (existingReceiptPreference === 'WeChat' || useMockEmail >= 0) ? 'WeChat' : 'Email';
}

// Set optedWeChat or optedEmail based on the server location
let optedWeChat = '';
let optedEmail = '';
if (serverLocation === 'CN') {
    optedWeChat = optedValue;
} else {
    optedEmail = optedValue;
}

// Prepare the output object
output = { finalReceiptPreference, optedWeChat, optedEmail };
