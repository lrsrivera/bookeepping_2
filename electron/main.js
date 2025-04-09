const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs').promises;

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    mainWindow.loadFile('electron/index.html');
    // Uncomment the following line to open DevTools by default
    // mainWindow.webContents.openDevTools();
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Handle file selection
ipcMain.handle('select-file', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [
            { name: 'Excel Files', extensions: ['xlsx', 'xls'] }
        ]
    });
    return result.filePaths[0];
});

// Handle processing request
ipcMain.handle('process-file', async (event, filePath) => {
    return new Promise((resolve, reject) => {
        const pythonScript = path.join(__dirname, '..', 'src', 'main.py');
        const pythonProcess = spawn('python', [pythonScript, filePath]);
        
        let output = '';
        let error = '';

        pythonProcess.stdout.on('data', (data) => {
            output += data.toString();
            mainWindow.webContents.send('processing-status', data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
            error += data.toString();
            mainWindow.webContents.send('processing-error', data.toString());
        });

        pythonProcess.on('close', async (code) => {
            if (code === 0) {
                // Read and send receipt contents
                await sendReceiptContents();
                resolve({ success: true, output });
            } else {
                reject({ success: false, error });
            }
        });
    });
});

// Function to read receipt contents
async function sendReceiptContents() {
    try {
        const outputDir = path.join(__dirname, '..', 'output');
        const files = await fs.readdir(outputDir);
        const receiptFiles = files.filter(file => file.startsWith('receipt_') && file.endsWith('.txt'));
        
        const receipts = await Promise.all(receiptFiles.map(async (file) => {
            const content = await fs.readFile(path.join(outputDir, file), 'utf-8');
            const dateMatch = file.match(/receipt_(\d{8})/);
            const date = dateMatch ? dateMatch[1] : '';
            const name = file.includes('various') ? 'Various Customer' : file.split('_').slice(2).join(' ').replace('.txt', '');
            
            return {
                name,
                date,
                content,
                filename: file  // Keep original filename for accurate sorting
            };
        }));
        
        // Sort receipts by date and then by filename (to maintain order for same date)
        const sortedReceipts = receipts.sort((a, b) => {
            if (a.date === b.date) {
                return a.filename.localeCompare(b.filename);
            }
            return a.date.localeCompare(b.date);
        });

        // Remove filename field before sending to frontend
        const cleanedReceipts = sortedReceipts.map(({ filename, ...rest }) => rest);
        
        mainWindow.webContents.send('receipt-update', cleanedReceipts);
    } catch (error) {
        console.error('Error reading receipts:', error);
    }
} 