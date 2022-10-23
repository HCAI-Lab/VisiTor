(defvar *mouse-pos* (vector 0 0))
(defvar pattern "")
(defvar *pattern-global* "")
(defvar keyString "")
(defvar command "")
(defvar input1 "")
(defvar input2 "")
;;File address

;; The directory
(defvar pythonaddress "c://Users//Amirreza//EyesNHands1//HeadsNtail.py")
;;==========================================================================================================================
(defvar Direc "c://Users//Amirreza//EyesNHandsfiles")
(ql:quickload 'inferior-shell)
(defmethod call-ShellCommand (command &optional arglist)
 (setq shell-request-list '())
  ;(print shell-request-list)
  ;(print "new list ")
(setq shell-request-list
 (append shell-request-list
 '("python")
 (list (symbol-value 'pythonaddress))
 (list (symbol-value 'command))
 '("--Dir")
(list (symbol-value 'Direc)) '("--arg2") arglist
))
; (print shell-request-list)
  (inferior-shell:run/ss shell-request-list )
  )

(defun what-is-on-screen (l)
;Match or MisMatch
  (setf command "whatisonscreen")
  (setq on-screen (call-ShellCommand command l))
;	(setf on-screen "tail")
  (act-r-output "what is on screen function ~A!!!" on-screen)
  on-screen)
(defun set-pattern (p)
  (setf *pattern-global* p)
;  (print "done!")
(act-r-output " Now we have ~s !!!!" *pattern-global*)
)

(defun respond-to-move-cursor (x y z)
(setf command "movecursortopattern")
(act-r-output "move-cursor to ~A!!!" z)
(act-r-output "first element ~A!!!" (nth 0 z))
;(print (get-key visual-list (list (nth 0 z)(nth 1 z))))
;list output
(act-r-output "Find in list move-cursor to ~a~%!!!" (get-key visual-list (list (nth 0 z)(nth 1 z))))
(setq result-from-java (call-ShellCommand command (list (get-key visual-list (list (nth 0 z)(nth 1 z))))))
)



(defun respond-to-click-mouse (x y z)
(setf command "click")
(setq result-from-java(call-ShellCommand command '("temp")))
(act-r-output "click a mouse!"))
(respond-to-click-mouse "temp" "temp" "temp")
(defun get-key (l sublist)
  "Finds a key given the pair of values associated with it"
  ;;l is the list
  ;;sublist if the associted sublist of the key
;  (print "working")
  (car (find-if (lambda (parts) (equal sublist (cadr parts))) l)))
;;Visual list
(defvar visual-list '())
;;visual-location ready
(push '(ready (0 0)) visual-list)
;;visual-location Tail
(push '(tail (10 10)) visual-list)
;;visual-location head
(push '(head (20 20)) visual-list)
;(inferior-shell:run ("python" "c:\\Users\\Amirreza\\EyesNHands\\HeadsNtail.py" "click"))
