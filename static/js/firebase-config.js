// Firebase 配置
// 注意：这是客户端配置，使用 Firebase 的公开 API Key
// 请从 Firebase Console > 项目设置 > 常规 > 您的应用 中获取实际配置
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "webstock-724.firebaseapp.com",
    projectId: "webstock-724",
    storageBucket: "webstock-724.firebasestorage.app",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// 初始化 Firebase
let db = null;

async function initFirebase() {
    if (db) return db;
    
    try {
        const app = firebase.initializeApp(firebaseConfig);
        db = firebase.firestore();
        console.log('✅ Firebase 初始化成功');
        return db;
    } catch (error) {
        console.error('❌ Firebase 初始化失败:', error);
        throw error;
    }
}

// 获取所有股票数据
async function getAllStocksFromFirebase() {
    const db = await initFirebase();
    
    try {
        const snapshot = await db.collection('stocks').get();
        const stocks = [];
        
        snapshot.forEach(doc => {
            stocks.push({
                code: doc.id,
                ...doc.data()
            });
        });
        
        console.log(`📊 从 Firebase 获取到 ${stocks.length} 只股票`);
        return stocks;
    } catch (error) {
        console.error('❌ 获取股票数据失败:', error);
        throw error;
    }
}

// 获取单只股票
async function getStockFromFirebase(code) {
    const db = await initFirebase();
    
    try {
        const doc = await db.collection('stocks').doc(code).get();
        
        if (doc.exists) {
            return {
                code: doc.id,
                ...doc.data()
            };
        } else {
            return null;
        }
    } catch (error) {
        console.error(`❌ 获取股票 ${code} 失败:`, error);
        throw error;
    }
}

// 搜索股票
async function searchStocksFromFirebase(keyword) {
    const stocks = await getAllStocksFromFirebase();
    
    const lowerKeyword = keyword.toLowerCase();
    return stocks.filter(stock => 
        stock.name?.toLowerCase().includes(lowerKeyword) ||
        stock.code?.includes(lowerKeyword) ||
        stock.concepts?.some(c => c.toLowerCase().includes(lowerKeyword))
    );
}

// 按概念筛选
async function getStocksByConceptFromFirebase(concept) {
    const db = await initFirebase();
    
    try {
        const snapshot = await db.collection('stocks')
            .where('concepts', 'array-contains', concept)
            .get();
        
        const stocks = [];
        snapshot.forEach(doc => {
            stocks.push({
                code: doc.id,
                ...doc.data()
            });
        });
        
        return stocks;
    } catch (error) {
        console.error(`❌ 获取概念 ${concept} 股票失败:`, error);
        throw error;
    }
}

// 导出函数供其他模块使用
window.FirebaseDB = {
    init: initFirebase,
    getAllStocks: getAllStocksFromFirebase,
    getStock: getStockFromFirebase,
    searchStocks: searchStocksFromFirebase,
    getStocksByConcept: getStocksByConceptFromFirebase
};
