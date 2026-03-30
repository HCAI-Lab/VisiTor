;;TODO: get visual value
;;!eval! with parameter
;; creat a seprate list for visual objects
;; 8/19/2018 add list for visual objects

(clear-all)

(defun do-experiment()
	(reset)
	(setf *pattern-global* "ready")
	;;visual-location ready	
	(add-visicon-features (list '(value ready) '(screen-x 0) '(screen-y 0) ))
	;;visual-location Tail
	(add-visicon-features (list '(value tail) '(screen-x 10) '(screen-y 10) ))
	;;visual-location head	
	(add-visicon-features (list '(value head) '(screen-x 20) '(screen-y 20) ))
	;;(chunk-type (player (:include visual-object)) name position turn result)
	 ;(install-device '("motor" "keyboard" ))
	 
	(add-act-r-command "my-move-cursor" 'respond-to-move-cursor "sth")
	(monitor-act-r-command "move-cursor" "my-move-cursor")
	(add-act-r-command "my-click-mouse" 'respond-to-click-mouse "sth")
	(monitor-act-r-command "click-mouse" "my-click-mouse")
	(install-device '("motor" "cursor" "mouse"))
	(start-hand-at-mouse)
	(run 1000)
	(remove-act-r-command-monitor "move-cursor" "my-move-cursor")
	(remove-act-r-command "my-move-cursor")
	(remove-act-r-command-monitor "click-mouse" "my-click-mouse")
	(remove-act-r-command "my-click-mouse")
)
(clear-all)


(define-model choice
;;first check for Ready
;;select head or tail
  (sgp :v t :trace-detail low :esc t  :show-focus t :ul t :ult t :needs-mouse t :MODEL-WARNINGS               NIL :egs 3)
  (buffer-chunk)
  (chunk-type try-strategy strategy state item)
;;(chunk-type encoding a-loc b-loc c-loc goal-loc length over under)
(define-chunks
    (goal isa try-strategy state start item blank)
    (start) (find-Head) (find-Tail) (looking) (attending)
    (choose-strategy) (move-attention-ready)
    (check-for-Ready) (finding) (whatisonscreen)
  (prepare-mouse) (move-mouse) (clicking)(blank) )

  
  (add-visicon-features '(screen-x 2 screen-y 2 value ready) )
  (add-visicon-features '(screen-x 10 screen-y 10  value tail))
  (add-visicon-features '(screen-x 20 screen-y 20  value head))
 ; (add-visicon-features (list '(screen-x 0) '(screen-y 0) '(value ready)))
  
 ; (add-visicon-features (list '(value tail) '(screen-x 10) '(screen-y 10) ))
 ; (add-visicon-features (list '(value head) '(screen-x 20) '(screen-y 20) ))
  
	;;visual-location Tail

;
	(add-act-r-command "my-move-cursor" 'respond-to-move-cursor "sth")
	(monitor-act-r-command "move-cursor" "my-move-cursor")
	(add-act-r-command "my-click-mouse" 'respond-to-click-mouse "temp" "temp" "sth")
	(monitor-act-r-command "click-mouse" "my-click-mouse")
	(install-device '("motor" "cursor" "mouse"))
  (start-hand-at-mouse)
  
;  	(remove-act-r-command-monitor "move-cursor" "my-move-cursor")
;	(remove-act-r-command "my-move-cursor")
;	(remove-act-r-command-monitor "click-mouse" "my-click-mouse")
;  (remove-act-r-command "my-click-mouse")
(goal-focus goal)
(p start-trial
   =goal>
      isa      try-strategy
      state    start
   ?visual-location>
      buffer   unrequested
  ==>
   =goal>
   state    check-for-Ready
;   !output!   ("hiii")
	)

(p check-for-Ready
   =goal>
      isa       try-strategy
      state     check-for-Ready
  ==>
   +visual-location>
      isa       visual-location
	  ;for a loop or non-stop search I should remove next line ":attended nil"
      :attended nil
    ;  value      ready
   =goal>
      state     move-attention
	  item "READY")
(p move-attention-ready
   =goal>
      isa        try-strategy
      state      move-attention
	  item "ready"
   =visual-location>
	  value 	ready
   ?visual>
      state      free
   ?manual>
	  state free
  ==>
 ;  !eval!(set-pattern =p)
   +visual>
      isa        move-attention
      screen-pos =visual-location
   +manual>
   isa move-cursor
	loc =visual-location
   =goal>
      state     choose-strategy)


(p tail

   =goal>
      ISA         try-strategy
      state       choose-strategy
  ; =visual>
   ;   value       ready

  ==>
   =goal>
      item        "tail"
      state       finding
   )


(p finding-tail
   =goal>
      isa       try-strategy
	  state finding
      item 		"tail"

  ==>
   +visual-location>
      isa       visual-location
    ;  :attended nil
      value      tail
   =goal>
      state     move-attention
	  item "tail"
)
(p head

   =goal>
      ISA         try-strategy
      state       choose-strategy
   ;=visual>
    ;  value       ready

  ==>
   =goal>
      item        "head"
      state       finding
   )

(p finding-head
   =goal>
      isa       try-strategy
	  state finding
      item 		"head"

  ==>
   +visual-location>
      isa       visual-location
     ; :attended nil
      value      head
   =goal>
      state     move-attention
	  item 	"head"
)
;Move attention to
(p move-attention
   =goal>
      isa        try-strategy
      state      move-attention
	  - item "ready"

   =visual-location>
	  ;value 	=a
   ?visual>
      state      free
   ?manual>
	  state free
  ==>
 ;  !eval!(set-pattern =p)
   +visual>
      isa        move-attention
      screen-pos =visual-location
   +manual>
   isa move-cursor
	loc =visual-location
   =goal>
      state      clicking)


(p clicking
   =goal>
      isa        try-strategy
      state      clicking
   ?manual>
      state      free
  ==>
   =goal>
      state      whatisonscreen
   +manual>
      isa        click-mouse)

	  ; (p find-on-screen
	; !bind! =x (what-is-on-screen)
	; +visual-location
	; value =x)

(p whatisonscreen
	  =goal>
      isa        try-strategy
      state      whatisonscreen
	  ?manual>
      state      free
	 ==>
	 !bind! =x (what-is-on-screen '("win" "lose"))
	  =goal>
	  isa 	try-strategy
	  state	attending
      item      =x
	)
(p match
   =goal>
      isa         try-strategy
      state       attending
      item        "win"
  ==>
   =goal>
	  State 	choose-strategy

	  )
(p mismatch
   =goal>
      isa         try-strategy
      state       attending
      item        "lose"
  ==>
   =goal>
	  State 	choose-strategy

	  )

(spp match :reward 6)
(spp mismatch :reward 0)
  )
(defvar visual-list '())
;;visual-location ready
(push '(ready (0 0)) visual-list)
;;visual-location Tail
(push '(tail (10 10)) visual-list)
;;visual-location head
(push '(head (20 20)) visual-list)
(run 1000)
;;For Visual object list
;;(run 1000)
;;(print-visicon)
;;(reset)
;;(printed-buffer-status 'visual-buffe)

(do-experiment)
