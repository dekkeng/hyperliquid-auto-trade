from time import mktime, gmtime, strftime, sleep
import utils

def currentTime(): 
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

def showAccountInfo():
    print("============================")
    print(currentTime(), "Current: "+str(balance_coin)+" " + config['coin'] + " | "+ str(balance_usd) + " USD")
    print("============================")

def checkBalance():
    global balances, balance_coin, balance_usd, last_ask

    balances = {}
    balance_coin = 0
    balance_usd = 0

    user_state = info.user_state(address)
    print(user_state)
    if user_state['assetPositions']:
        for ps in user_state['assetPositions']:
            p = ps['position']
            balances[p['coin'].upper()] = {
                "szi": float(p['szi']),
                "entryPx": float(p['entryPx']),
                "limit": 0,
            }

    if config['coin'] in balances:
        balance_coin = balances[config['coin']]['szi']
        if last_ask == 0: 
            last_ask = balances[config['coin']]['entryPx']

    if user_state['marginSummary']['totalRawUsd']:
        balance_usd = user_state['marginSummary']['totalRawUsd']

def main():
    global config, address, info, exchange, last_ask, last_time
    config, address, info, exchange = utils.setup(skip_ws=True)
    last_ask = 0
    last_time = mktime(gmtime())    
    checkBalance()
    showAccountInfo()    
    print(exchange.update_leverage(1, config['coin']))
    worker_simple()

def worker_simple():
    checkBalance()
    showAccountInfo()
    if balance_coin > 0:
        print(f"======= CLOSING ALL {config['coin']} ORDER ======")
        order_result = exchange.market_close(config['coin'])
        if order_result["status"] == "ok":
            for status in order_result["response"]["data"]["statuses"]:
                try:
                    filled = status["filled"]
                    print(currentTime(), f'Order #{filled["oid"]} filled {filled["totalSz"]} @{filled["avgPx"]}')
                except KeyError:
                    print(currentTime(), f'Error: {status["error"]}')
    else:
        print(f"======= BUYING {config['coin']} ORDER ======")
        order_result = exchange.market_open(config['coin'], True, config['size'], None, config['slippage'])
        if order_result["status"] == "ok":
            for status in order_result["response"]["data"]["statuses"]:
                try:
                    filled = status["filled"]
                    print(currentTime(), f'Order #{filled["oid"]} filled {filled["totalSz"]} @{filled["avgPx"]}')
                except KeyError:
                    print(currentTime(), f'Error: {status["error"]}')
    
    sleep(10)
    worker_simple()

def worker():
    checkBalance()
    showAccountInfo()
    if balance_coin > 0:
        print(currentTime(), "Waiting " + str(config['price_decrease_interval']) + " mins | Selling "+ str(balance_coin) + " "+config['coin'] + " at $"+str(balances[config['coin']]['limit']) +" ("+ str(balances[config['coin']]['limit'] * str(balance_coin)) + " USD)...");   
        while (balance_coin > 0):
            now = mktime(gmtime())
            if( (now - last_time) > (config['price_decrease_interval']*60000) ):
                last_ask = last_ask - (config['price_diff'] * (config['price_decrease_percent']) / 100)
                print("Cancel order, decrease sell price ("+config['price_decrease_percent']+"%) to $"+last_ask)
                close_order()
            else:
                sleep(3)
            checkBalance()
    else:
        open_order()

def close_order():
    global last_time
    print("======= CLOSING ORDER ======")
    checkBalance()

    # if last_ask == 0:
    #     let {lastPrice: ask} = await client.Ticker({ symbol: SYMBOL });
    #     lastPriceAsk = ask;

    szi = balance_coin*0.95
    print(currentTime(), "Sell limit "+szi+" "+config['coin']+" at $"+last_ask+ " ($"+(last_ask * szi)+ " USD)")

    # set limit to order
    order_result = exchange.market_close(config['coin'], False, szi, None, 0.01)
    last_time = mktime(gmtime())

    if order_result["status"] == "ok":
        for status in order_result["response"]["data"]["statuses"]:
            try:
                filled = status["filled"]
                print(currentTime(), "Sold "+filled["totalSz"]+" "+config['coin'] + " at $"+filled["avgPx"] +" , Order number: "+filled["oid"])
                last_ask = 0
                worker()
            except KeyError:
                print(f'Error: {status["error"]}')

def open_order():
    global last_ask
    print("======= BUYING ======")
    checkBalance()
    szi = 0.01
    order_result = exchange.market_open(config['coin'], True, szi, None, 0.01)
    if order_result["status"] == "ok":
        for status in order_result["response"]["data"]["statuses"]:
            try:
                filled = status["filled"]
                print(currentTime(), "Bought "+filled["totalSz"]+" "+config['coin'] + " at $"+filled["avgPx"] +" , Order number: "+filled["oid"])
                last_ask = filled["avgPx"] + config['price_diff']
                worker()
            except KeyError:
                print(f'Error: {status["error"]}')

if __name__ == "__main__":
    main()


# function showAccountInfo() {    
#     console.log("============================")
#     console.log(getNowFormatDate(), `My Balance: ${balance_1} ${symbol_1} | ${balance_2} ${symbol_2}`);
#     console.log("============================")
# }
# const checkBalance = async (client) => {
#     userbalance = await client.Balance();
#     balance_1 = 0 
#     if (userbalance[symbol_1]) {
#         balance_1 = userbalance[symbol_1].available
#     }
#     balance_2 = 0;
#     if (userbalance[symbol_2]) {
#         balance_2 = userbalance[symbol_2].available
#     }
# }
# const worker = async (client) => {
#     try {
#         let GetOpenOrders = await client.GetOpenOrders({ symbol: SYMBOL });
#         if(GetOpenOrders.length > 0) {
#             if(lastPriceAsk == 0) lastPriceAsk = GetOpenOrders[0].price;
#             console.log(getNowFormatDate(), `Waiting ${PRICE_DECREASE_INTERVAL} mins | Selling ${GetOpenOrders[0].quantity} ${symbol_1} at $${GetOpenOrders[0].price} (${(GetOpenOrders[0].price * GetOpenOrders[0].quantity).toFixed(2)} ${symbol_2})...`);    
#             while (GetOpenOrders.length > 0) {
#                 let now = new Date().getTime();
#                 if( (now - lastPriceTime) > (PRICE_DECREASE_INTERVAL*60000) ) {
#                     lastPriceAsk = lastPriceAsk - (PRICE_DIFF * (PRICE_DECREASE_PERCENT) / 100);
#                     console.log(`Cancel order, decrease sell price (${PRICE_DECREASE_PERCENT}%) to $${lastPriceAsk}`);
#                     await client.CancelOpenOrders({ symbol: SYMBOL });
#                 } else {
#                     await delay(3000);
#                 }
#                 GetOpenOrders = await client.GetOpenOrders({ symbol: SYMBOL });
#             }
#         }

#         await checkBalance(client);

#         if (balance_2 > MIN_SYMBOL_2) {
#             await buyfun(client);
#         } else {
#             await sellfun(client);
#         }
#     } catch (e) {
#         console.log(getNowFormatDate(), `Try again... (${e.message})`);

#         await delay(3000);
#         worker(client);

#     }
# }

# const sellfun = async (client) => {
#     console.log("======= SELLING ======");
#     await checkBalance(client);
#     if (balance_1 < MIN_SYMBOL_1) {
#         throw new Error(`Insufficient balance (${balance_1} ${symbol_1}) | Retrying...`);
#     } else {
#         if(lastPriceAsk == 0) {
#             let {lastPrice: ask} = await client.Ticker({ symbol: SYMBOL });
#             lastPriceAsk = ask;
#         }
#         lastPriceAsk = (lastPriceAsk*1).toFixed(2);
#         let quantitys = (userbalance[symbol_1].available - 0.02).toFixed(2).toString();
#         console.log(getNowFormatDate(), `Sell limit ${quantitys} ${symbol_1} at $${lastPriceAsk} (${(lastPriceAsk * quantitys).toFixed(2)} ${symbol_2})`);
#         let orderResultAsk = await client.ExecuteOrder({
#             orderType: "Limit",
#             price: lastPriceAsk.toString(),
#             quantity: quantitys,
#             side: "Ask",
#             symbol: SYMBOL,
#             timeInForce: "GTC"
#         })
#         lastPriceTime = new Date().getTime();
#         worker(client);
#     }
# }

# const buyfun = async (client) => {
#     console.log("======= BUYING ======");
#     await checkBalance(client);
#     let {lastPrice: lastBuyPrice} = await client.Ticker({ symbol: SYMBOL });
#     let quantitys = ((userbalance[symbol_2].available - 2) / lastBuyPrice).toFixed(2).toString();
#     let orderResultBid = await client.ExecuteOrder({
#         orderType: "Limit",
#         price: lastBuyPrice.toString(),
#         quantity: quantitys,
#         side: "Bid",
#         symbol: SYMBOL,
#         timeInForce: "IOC"
#     })
#     if (orderResultBid?.status == "Filled" && orderResultBid?.side == "Bid") {
#         console.log(getNowFormatDate(), `Bought ${quantitys} ${symbol_1} at $${lastBuyPrice} ${symbol_2}`, `Order number: ${orderResultBid.id}`);
#         lastPriceAsk = lastBuyPrice + PRICE_DIFF;
#         showAccountInfo();
#         worker(client);
#     } else {
#         if (orderResultBid?.status == 'Expired'){
#             throw new Error(`Buying ${quantitys} ${symbol_1} at $${lastBuyPrice} ${symbol_2} Expired | Retrying...`);
#         } else{
#             throw new Error(orderResultBid?.status);
#         }
#     }
# }

# (async () => {
#     const apisecret = API_SECRET;
#     const apikey = API_KEY;
#     const client = new backpack_client_1.BackpackClient(apisecret, apikey);
#     await checkBalance(client);
#     showAccountInfo();
#     worker(client);
# })()