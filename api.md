**Flask API**
----

* **URL**

  api/

* **Method:**

  `GET`

* **Sample Call 1:**

   * headers-
   
      content-type:application/json

   * endpoint-
    
      api/list
   
* **Sample response 1:**
```json
  {
    desc:["ration card distribution [...] ","driver license for free [...]"]
    image:["asjldkjlajsfdlk","asdasfwedfasf"]
  }
```
  
* **Notes:**

  The above call returns 2 lists of size n containing one line desc and img of n schemes.
  
  The one line description ,one img(base64 encoded) of a scheme i is in desc[i],image[i]
  
* **Sample Call 2:**
   
   * headers-
   
      content-type:plain-text/html

   * endpoint-
    
      api/scheme0/content
   

* **Sample response 2:**

    contains json in plain-text/html having the follwing structure,j indicating the the paritcular element number-
```json
  {
        h1<j>:"heading"
        h2<j>:"sub heading"
        h3<j>:"samller sub heading"
        src<j>:"contains link for img "
        text<j>: "contains a line or a paragraph"
        center<j>:"dipaly text in center of screen"
        small<j>:"display in a smaller size"
        table_<a>_tr_<b>_td_<c>_text_:"text of table a , row b, col c text"
        table_<a>_tr_<b>_td_<c>_centre_text_:"same as previous but text in centre"
        table_<a>_tr_<b>_td_<c>_small_text_:"display in a smaller size"
        table_<a>_tr_<b>_th_<c>_text_:"contains attribute c of a table"
        table_<a>_tr_<b>_th_<c>_centre_text_:"attribute c of a table to be diaplayed in centre"
        table_<a>_tr_<b>_td_<c>_small_text_:"display in a smaller size"
        
  }
```
* **Notes:**
 
  1.Data may contain escape sequences. 
  
  2.Possibilty of getting ``table_<a>_tr_<b>_td_<c>_centre_text_``  as  ``table_<a>_tr_<b>_td_<c>_text_centre_``.
  
  3.response for call 2 is sent as plain-text to maintine order of the elements.
  
  
 
 
