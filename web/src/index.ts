// (base: https://www.typescriptlang.org/play/)
const jsQR = require("jsqr");
import 'normalize.css'
import "./index.scss"
import DCC from "./dcc_class";
import { Vaccination } from './dcc_class';
import { Recovery } from './dcc_class';



const app = document.getElementById("app");
const video = document.createElement("video");
const canvasWrapper = document.createElement("div");
const infoText = document.createElement("div");
const canvasElement = <HTMLCanvasElement>document.createElement("canvas");
const ctx = canvasElement.getContext("2d");
const validationResult = document.createElement("div");
const scanButton = document.createElement("button");

infoText.setAttribute("id", "info");
canvasWrapper.setAttribute("id", "canvaswrapper");
validationResult.setAttribute("id", "result");

scanButton.innerText = "Resume scan";
infoText.innerHTML = "Waiting for camera device...";

canvasWrapper.appendChild(canvasElement);
canvasWrapper.appendChild(infoText);
app?.appendChild(canvasWrapper);
app?.appendChild(validationResult);
app?.appendChild(scanButton);
let codeFound: boolean = false;
let lastCode: string = "";

async function postData(url: string = '', data: any = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: 'POST',
    mode: 'cors',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json'
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    body: JSON.stringify(data)
  });
  return response; // parses JSON response into native JavaScript objects
}

function resumeScan() {
  video.play();
  codeFound = false;
  canvasWrapper.classList.remove('valid');
  canvasWrapper.classList.remove('invalid');
  canvasWrapper.classList.remove('hidden');
  validationResult.innerHTML = "";
  infoText.innerHTML = "Scan an EU Covid Certificate now."
  scanButton.classList.add('hidden');
  lastCode = "";
}
scanButton.addEventListener("click", resumeScan);

function requestValidation(code: string): void {
  postData('/', { "dcc": code }).then(response => response.json().then(data => {
    showValidationResult(data);
    scanButton.classList.add('visible');
  }
  ).catch((error) => {
    console.log(error);
    validationResult.innerHTML = "Could not submit code to server!";
  }
  )
  );
};

function createInfoTableRow(target: HTMLElement, id: string, label: string = "", content: string | number) {

  let row = document.createElement("tr");
  row.classList.add('row');
  row.id = id;
  row.innerHTML = '<td class="label">' + label + '</td><td class="content">' + content + '</td>'
  target.appendChild(row);
}

function prepareResults(json: any): HTMLElement | void {
  const dcc = new DCC().deserialize(json);
  console.log(dcc)
  let table = document.createElement("table");
  table.classList.add("info-table");

  if (dcc.valid) {
    table.classList.add("valid");
  }

  createInfoTableRow(table, "validity", "Valid", String(dcc.valid));
  createInfoTableRow(table, "issuerCountry", "Issuer Country", dcc.issuerCountry);
  let date = new Date(dcc.issueDate * 1000);
  createInfoTableRow(table, "issueDate", "Issue Date", date.toISOString());
  date = new Date(dcc.expirationDate * 1000);
  createInfoTableRow(table, "expirationDate", "Expiration Date", date.toISOString());

  for (let key in dcc.certificates) {
    let certificate: any = dcc.certificates[key];
    createInfoTableRow(table, "name", "Full name", certificate.name.getFullName());
    createInfoTableRow(table, "dob", "Date of Birth", certificate.dob);
    if (typeof certificate.vaccination != undefined) {
      createInfoTableRow(table, "certtype", "Certificate Type", "Vaccination");
      createInfoTableRow(table, "date", "Date", certificate.vaccination.date);
      createInfoTableRow(table, "country", "Country", certificate.vaccination.country);
      createInfoTableRow(table, "issuer", "Issuer", certificate.vaccination.issuer);
      createInfoTableRow(table, "doseNumber", "Dose Number", certificate.vaccination.doseNumber);
      createInfoTableRow(table, "uvci", "UVCI", certificate.vaccination.uvci);
    } else
      if (typeof certificate.test != undefined) {
        createInfoTableRow(table, "certtype", "Certificate Type", "Test");
        createInfoTableRow(table, "result", "Result", certificate.test.result);
        createInfoTableRow(table, "date", "Date", certificate.test.date);
        createInfoTableRow(table, "country", "Country", certificate.test.country);
        createInfoTableRow(table, "issuer", "Issuer", certificate.test.issuer);
        createInfoTableRow(table, "uvci", "UVCI", certificate.vaccination.uvci);
      } else
        if (typeof certificate.recovery != undefined) {
          createInfoTableRow(table, "certtype", "Certificate Type", "Recovery");
          createInfoTableRow(table, "firstPositiveDate", "Date", certificate.recovery.firstPositiveTestDate);
          createInfoTableRow(table, "country", "Country", certificate.recovery.country);
          createInfoTableRow(table, "issuer", "Issuer", certificate.recovery.issuer);
          date = new Date(certificate.recovery.validFrom * 1000);
          createInfoTableRow(table, "validFrom", "Valid from", date.toISOString());
          date = new Date(certificate.recovery.validUntil * 1000);
          createInfoTableRow(table, "validUntil", "Valid until", date.toISOString());
          createInfoTableRow(table, "uvci", "UVCI", certificate.vaccination.uvci);
        }
  }


  validationResult.appendChild(table);


}


function showValidationResult(json: any): void {
  console.log("Code validation request complete.")
  console.log("Result:", json);
  if (json.valid) {
    console.log("Certificate is VALID.")
    prepareResults(json);
    video.pause();
    canvasWrapper.classList.add("hidden");
  } else {
    console.log("Certificate is INVALID.")
    canvasWrapper.classList.add('invalid')
    codeFound = false;
    validationResult.innerHTML = "This certificate is invalid!";
    validationResult.classList.add("error");
  }
}


function tick(): void {
  if (video.readyState === video.HAVE_ENOUGH_DATA) {
    canvasElement.hidden = false;

    canvasElement.height = video.videoHeight;
    canvasElement.width = video.videoWidth;
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);
      var imageData = ctx.getImageData(0, 0, canvasElement.width, canvasElement.height);
      let code: any = false;
      if (!codeFound) {
        code = jsQR(imageData.data, imageData.width, imageData.height, {
          inversionAttempts: "dontInvert",
        });
      }

      if (code) {
        console.log("Code found containing:", code);
        // Check if there is a possibility of this being a valid certificate before sending to server
        if (code.data.startsWith("HC1:")) {
          console.log("Possible DCC found.")
          if (lastCode != code.data) {
            console.log("This is not the same certificate as before. Trying to validate.")
            canvasWrapper.classList.remove('invalid')
            validationResult.innerHTML = "";
            validationResult.classList.remove('error');
            codeFound = true;
            lastCode = code.data;
            requestValidation(code.data);
          } else {
            console.log("This is the same certificate as before. Not submitting.")
          }
        } else {
          console.log("Code found, but certainly not a DCC.")
          canvasWrapper.classList.add('invalid')
          validationResult.innerHTML = "This is not an EU Covid Certificate.";
          validationResult.classList.add('error');
          codeFound = false;
          lastCode = code.data;
        }
      }
    }
  }
  requestAnimationFrame(tick);
}


// Use facingMode: environment to attemt to get the front camera on phones
navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(function (stream) {
  video.srcObject = stream;
  video.setAttribute("playsinline", 'true'); // required to tell iOS safari we don't want fullscreen
  video.play();
  infoText.innerHTML = "Scan an EU Covid Certificate now."
  infoText.classList.add("top");
  requestAnimationFrame(tick);
});

