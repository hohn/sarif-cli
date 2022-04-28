/**
 * @name metrics01
 * @description short sample
 * @kind diagnostic
 * @id cpp/diagnostics/metrics01
 */

import cpp

select count(File f | f.fromSource()).toString()
