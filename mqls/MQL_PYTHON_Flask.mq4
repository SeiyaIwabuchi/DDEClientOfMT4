//+------------------------------------------------------------------+
//|                                             MQL_PYTHON_Flask.mq4 |
//|                        Copyright 2019, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2019, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict
//+------------------------------------------------------------------+
//|                                             MQL_PYTHON_Flask.mq5 |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//---
  string cookie=NULL,headers;
  char   post[],result[];
//  string url="http://localhost/oanda?open=1.5555&high=1.6666&low=1.7777&close=1.8888";
  string url="http://localhost";

  ResetLastError();

  int res=WebRequest("GET",url,cookie,NULL,500,post,0,result,headers);
  if(res==-1)
    {
    Print("Error in WebRequest. Error code  =",GetLastError());
    //MessageBox("Add the address '"+url+"' to the list of allowed URLs on tab 'Expert Advisors'","Error",MB_ICONINFORMATION);
    }
  else
    {
    if(res==200)
       {
        string target = CharArrayToString(result);
        Print("========="+target+"=========");
       }
    else
      {
        PrintFormat("Request '%s' failed, error code %d",url,res);
      }
    }
//---
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+

void OnTick(){
   RefreshRates();
   Print("Bid:"+Bid);
   Print("Ask"+Ask);
   string cookie=NULL,headers;
   char   post[],result[];
//  string url="http://localhost/oanda?open=1.5555&high=1.6666&low=1.7777&close=1.8888";
   string url="http://localhost";
   
   int res=WebRequest("GET","http://localhost/sendTick?bid="+Bid+"&ask="+Ask+"&datetime="+TimeCurrent(),cookie,NULL,500,post,0,result,headers);
   if (res == -1){
      Print("Tick send error");
      int retryTime = 0;
      while(res == -1 && retryTime < 10){
         retryTime++;
         Print("Retry" + retryTime);
         res=WebRequest("GET","http://localhost/sendTick?bid="+Bid+"&ask="+Ask+"&datetime="+TimeCurrent(),cookie,NULL,500,post,0,result,headers);
         if (retryTime == 10) Print("Retry Failed");
      }
      string target = CharArrayToString(result);
      Print("Retry " + target);
   }else{
      string target = CharArrayToString(result);
      Print(target);
   }
}