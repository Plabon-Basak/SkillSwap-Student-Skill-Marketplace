import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'

import { getErrorMessage } from '@/api/client'
import { Avatar } from '@/components/common/Avatar'
import { Button } from '@/components/common/Button'
import { Alert, ErrorState, LoadingState } from '@/components/common/Feedback'
import { useAuth } from '@/hooks/useAuth'
import { messagingApi } from '@/services/messaging'
import { formatRelative } from '@/utils/format'

export function ConversationPage() {
  const { threadId } = useParams<{ threadId: string }>()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [body, setBody] = useState('')
  const [sendError, setSendError] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  const { data: thread, isLoading: threadLoading, isError } = useQuery({
    queryKey: ['thread', threadId],
    queryFn: () => messagingApi.thread(Number(threadId)),
    enabled: Boolean(threadId),
  })

  const { data: messages, isLoading: messagesLoading } = useQuery({
    queryKey: ['messages', threadId],
    queryFn: () => messagingApi.messages(Number(threadId)),
    enabled: Boolean(threadId),
    refetchInterval: 5_000,
  })

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const sendMessage = useMutation({
    mutationFn: (text: string) => messagingApi.sendMessage(Number(threadId), text),
    onSuccess: () => {
      setBody('')
      setSendError(null)
      void queryClient.invalidateQueries({ queryKey: ['messages', threadId] })
      void queryClient.invalidateQueries({ queryKey: ['threads'] })
    },
    onError: (error) => setSendError(getErrorMessage(error)),
  })

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    const text = body.trim()
    if (!text) return
    sendMessage.mutate(text)
  }

  if (threadLoading || messagesLoading) return <LoadingState />
  if (isError || !thread) return <ErrorState message="Conversation not found." />

  const others = [thread.buyer, thread.provider]

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-4 flex items-center justify-between">
        <Link to="/messages" className="text-sm text-primary-600 hover:text-primary-700">
          ← All conversations
        </Link>
        <p className="text-sm text-gray-500">
          Order #{thread.order} ·{' '}
          {others.map((p) => p.display_name).join(' × ')}
        </p>
      </div>

      <div>
        <div
          ref={scrollRef}
          className="h-[60vh] space-y-3 overflow-y-auto rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
          aria-live="polite"
        >
          {messages?.map((message) => {
            const mine = message.sender.username === user?.username
            return (
              <div
                key={message.id}
                className={`flex gap-2 ${mine ? 'flex-row-reverse' : ''}`}
              >
                <Avatar src={message.sender.avatar} name={message.sender.display_name} size="sm" />
                <div
                  className={`max-w-[75%] rounded-lg px-3 py-2 text-sm shadow-sm ${
                    mine
                      ? 'rounded-tr-none bg-primary-600 text-white'
                      : 'rounded-tl-none bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="whitespace-pre-line">{message.body}</p>
                  <p
                    className={`mt-1 text-[11px] ${
                      mine ? 'text-primary-100' : 'text-gray-400'
                    }`}
                  >
                    {formatRelative(message.created_at)}
                  </p>
                </div>
              </div>
            )
          })}
        </div>

        {sendError && (
          <div className="mt-3">
            <Alert variant="error">{sendError}</Alert>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-3 flex gap-2">
          <input
            type="text"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Type a message…"
            maxLength={2000}
            className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            aria-label="Message body"
          />
          <Button type="submit" loading={sendMessage.isPending} disabled={!body.trim()}>
            Send
          </Button>
        </form>
      </div>
    </div>
  )
}