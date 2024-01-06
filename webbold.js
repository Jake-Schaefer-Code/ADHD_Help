
/** 
 * "javascript:" informs browser that the code is in javascript
 * "(function() { ... })" immediately invoked expression (IIFE) 
 *      -> creates a function and executes it immediately after its definition
 *      -> helps prevent variable names and functions defined in the script from conflicting with those in the global scope
*/
javascript:(function() {
    var elements = document.querySelectorAll('*:not(script):not(style):not(meta):not(link):not(title):not(head):not(html)')
    document.body.style.fontFamily = 'Arial, sans-serif';
    elements.forEach(function(element) {
        element.childNodes.forEach(function(child){
            if (child.nodeType === 3) {
                
                var textContent = child.nodeValue;
                // nodeTpe === 3 means a text node
                
                var words = textContent.split(/\b/);
                var modifiedWords = words.map(function(word) {
                    if (word.trim() !== '') {
                        var mid = Math.ceil(word.length / 2);
                        if (word.length > 3) {
                            return '&nbsp' + '<b>' + word.substring(0, mid) + '</b>' + word.substring(mid);
                        } else if (/\$.*?\$|\(.*?\)/.test(word) || /^[-,/:;.]+$/.test(word)) {
                            return word;
                        } else if (word.length === 1){
                            if (element.tagName.toLowerCase() === 'i') {
                                return word;
                            } else {
                                return '&nbsp' + word;
                            }
                        } else {
                            // Find a way to change the space size rather than add another
                            return '&nbsp' + word;
                        }
                        
                    } else {
                        return word; // Preserve spaces
                    }
                });
                var span = document.createElement('span');
                span.innerHTML = modifiedWords.join('');
                child.replaceWith(span);
            }
        });
    });
})();


/**
 * var isSpace = true;
 * for (var i = 0; i < originalText.length; i++) {
                    var char = originalText.charAt(i);
                    if (char === ' ') {
                        modifiedText += char;
                        isSpace = true;
                    } else {
                        var mid = isSpace ? 0 : Math.ceil(char.length / 2);
                        modifiedText += '<b>' +char.substring(0, mid) + '</b>' + char.substring(mid);
                        isSpace = false;
                    }
                }
 */